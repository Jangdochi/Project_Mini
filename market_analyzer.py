import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import sqlite3
import os
from datetime import datetime, timedelta
import scipy.stats as stats




# [1] 데이터베이스 경로 설정
db_path_1 = 'data/news_scraped.db'
db_path_2 = 'data/news.db'


def get_data_from_db(db_path):
    """DB에서 데이터를 가져오고 테이블 이름 및 건수 확인"""
    try:
        if not os.path.exists(db_path):
            print(f"⚠️ 파일 없음: {db_path}")
            return pd.DataFrame()
       
        conn = sqlite3.connect(db_path)
        # [주석] 데이터가 왜 적은지 확인하기 위해 'is_processed' 조건을 제거하고 전체를 봅니다.
        query = "SELECT published_time, sentiment_score, is_processed FROM news"
        df = pd.read_sql(query, conn)
        conn.close()
       
        if not df.empty:
            processed_count = df[df['is_processed'] == 1].shape[0]
            print(f"📊 {db_path} 로드 완료: 총 {len(df)}건 (처리완료: {processed_count}건)")
        else:
            print(f"⚠️ {db_path} 내부에 데이터가 아예 없습니다.")
        return df
    except Exception as e:
        print(f"❌ {db_path} 로드 실패: {e}")
        return pd.DataFrame()


# [2] 데이터 로드 및 통합
df_db1 = get_data_from_db(db_path_1)
df_db2 = get_data_from_db(db_path_2)


# [주석] 두 DB 데이터를 합칩니다.
valid_dfs = [df for df in [df_db1, df_db2] if not df.empty]
if not valid_dfs:
    print("❌ 로드된 데이터가 전혀 없습니다.")
    exit()


df_news_raw = pd.concat(valid_dfs, ignore_index=True)


# [3] 데이터 정제
df_analysis = df_news_raw.copy()
# 날짜 변환
df_analysis['published_time'] = pd.to_datetime(df_analysis['published_time'], errors='coerce')
df_analysis = df_analysis.dropna(subset=['published_time'])


# 날짜별 평균 점수 계산 (전체 데이터 대상)
df_analysis['date'] = df_analysis['published_time'].dt.date
df_daily_sentiment = df_analysis.groupby('date')['sentiment_score'].mean().reset_index()


# [4] 날짜 범위 설정 (최근 30일)
today = datetime.now().date()
one_month_ago = today - timedelta(days=30)


# [주석] 필터링 전 전체 범위를 다시 출력해서 확인합니다.
print(f"🔍 통합 데이터 전체 범위: {df_daily_sentiment['date'].min()} ~ {df_daily_sentiment['date'].max()}")


# 최근 한 달치로 필터링
df_daily_sentiment = df_daily_sentiment[df_daily_sentiment['date'] >= one_month_ago]


# [5] 주식 시장 데이터 및 수익률 계산
start_fdr = (one_month_ago - timedelta(days=10)).strftime('%Y%m%d')
end_fdr = today.strftime('%Y%m%d')


try:
    kospi = fdr.DataReader('KS11', start_fdr, end_fdr)[['Close']].rename(columns={'Close': 'KOSPI'})
    kosdaq = fdr.DataReader('KQ11', start_fdr, end_fdr)[['Close']].rename(columns={'Close': 'KOSDAQ'})
   
    kospi_ret = kospi.pct_change() * 100
    kosdaq_ret = kosdaq.pct_change() * 100
   
    for df in [kospi_ret, kosdaq_ret]:
        df.index = pd.to_datetime(df.index).date
   
    df_market_ret = pd.concat([kospi_ret, kosdaq_ret], axis=1)
    df_final = pd.merge(df_daily_sentiment, df_market_ret, left_on='date', right_index=True, how='left')
except Exception as e:
    print(f"⚠️ 주식 연동 오류: {e}")
    df_final = df_daily_sentiment


# [6] 결과 출력
df_final.columns = ['날짜', '뉴스감성점수', 'KOSPI수익률(%)', 'KOSDAQ수익률(%)']


print("\n" + "="*75)
print(f"   [분석 리포트] 최근 30일 (데이터가 있는 날짜 모두 출력)   ")
print("="*75)
print(df_final.sort_values(by='날짜', ascending=False))
print("="*75)


# [1] 상관계수 계산 (Pearson Correlation)
# [주석] -1에 가까우면 반비례, 1에 가까우면 정비례, 0에 가까우면 관계없음을 뜻합니다.
# 주말(NaN) 데이터를 제외하고 계산합니다.
clean_df = df_final.dropna()


kospi_corr = clean_df['뉴스감성점수'].corr(clean_df['KOSPI수익률(%)'])
kosdaq_corr = clean_df['뉴스감성점수'].corr(clean_df['KOSDAQ수익률(%)'])


# [2] 감성 점수 구간별 평균 수익률 (통계적 유의성 확인)
# [주석] 감성 점수를 '부정(0.4 미만)', '중립(0.4~0.6)', '긍정(0.6 초과)'으로 나누어 분석합니다.
def get_sentiment_group(score):
    if score > 0.6: return '긍정(High)'
    elif score < 0.5: return '부정(Low)'
    else: return '중립(Mid)'


clean_df['감성구간'] = clean_df['뉴스감성점수'].apply(get_sentiment_group)
stats_analysis = clean_df.groupby('감성구간')[['KOSPI수익률(%)', 'KOSDAQ수익률(%)']].mean()


# [3] 결과 출력
print("\n" + "="*75)
print("   [통계 분석 결과] 뉴스 감성과 시장 수익률의 관계   ")
print("="*75)
print(f"📈 [상관계수] 뉴스 점수 ↔ KOSPI : {kospi_corr:.4f}")
print(f"📈 [상관계수] 뉴스 점수 ↔ KOSDAQ: {kosdaq_corr:.4f}")
print("-" * 75)
print("📊 [구간별 평균 수익률 통계]")
print(stats_analysis)
print("="*75)


# [주석] 상관계수 해석 가이드
if abs(kospi_corr) > 0.15:
    print("💡 해석: 뉴스 점수와 KOSPI 사이에 유의미한 관계가 관찰됩니다.")
else:
    print("💡 해석: 뉴스 점수와 지수 간의 직접적인 선형 관계는 다소 약합니다.")
