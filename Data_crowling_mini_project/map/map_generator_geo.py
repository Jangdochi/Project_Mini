import os
import json
import folium
from folium import IFrame, GeoJson
from folium.features import DivIcon
from typing import List, Dict
import html

# 기존 모듈 임포트 (경로 및 환경에 맞춰 유지)
from db_loader import NewsDBLoader
from region_coords import KOREA_CENTER, DEFAULT_ZOOM, REGION_COORDS
from color_mapper import get_sentiment_label
from region_mapper import get_db_region


class NewsMapGeneratorGeo:
    """GeoJSON 기반 뉴스 지도 생성기 (부정 기사 비율 기준 버전)"""
    
    REGION_CONSOLIDATION = {
        '서울': ['서울'],
        '경기도': ['경기도', '인천'],
        '강원도': ['강원도'],
        '충청도': ['충청도'],
        '경상도': ['경상도', '경남', '경북'],
        '전라도': ['전라도', '전남']
    }

    ECON_KEYWORDS = [
        '경제', '증시', '주가', '코스피', '코스닥', '환율', '금리', '물가', '인플레이션',
        '금융', '은행', '대출', '채권', '시장', '투자', '기업', '산업', '경기', '성장',
        '수출', '수입', '무역', '부동산', '주택', '아파트', '매출', '실적', '영업이익',
        '적자', '흑자', '세금', '재정'
    ]
    
    def __init__(self, db_path: str = None, geojson_path: str = None):
        self.loader = NewsDBLoader(db_path)
        if geojson_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            geojson_path = os.path.join(os.path.dirname(current_dir), 'skorea-provinces-geo.json')
        
        self.geojson_path = geojson_path
        self.geojson_data = None
        self.map = None
        
    def load_geojson(self):
        try:
            with open(self.geojson_path, 'r', encoding='utf-8') as f:
                self.geojson_data = json.load(f)
            print(f"✅ GeoJSON 로드 완료: {len(self.geojson_data.get('features', []))}개 지역")
            return True
        except Exception as e:
            print(f"❌ GeoJSON 로드 실패: {e}")
            return False
    
    def create_map(self):
        self.map = folium.Map(
            location=KOREA_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles='OpenStreetMap',
            control_scale=True
        )
        return self.map
    
    def get_region_statistics(self):
        """각 지역의 통계 계산"""
        db_stats = self.loader.get_region_stats()
        consolidated_stats = {}
        
        for main_region, db_regions in self.REGION_CONSOLIDATION.items():
            total_count = 0
            total_positive = 0
            total_negative = 0
            
            for db_region in db_regions:
                if db_region in db_stats:
                    stat = db_stats[db_region]
                    total_count += stat['count']
                    total_positive += stat['positive_count']
                    total_negative += stat['negative_count']
            
            # 부정 기사 비율 계산 (%)
            neg_ratio = (total_negative / total_count * 100) if total_count > 0 else 0
            
            consolidated_stats[main_region] = {
                'count': total_count,
                'positive_count': total_positive,
                'negative_count': total_negative,
                'negative_ratio': neg_ratio
            }
        return consolidated_stats

    def _split_keywords(self, keyword_text: str) -> List[str]:
        if not keyword_text: return []
        separators = [',', '|', '/', ';']
        normalized = keyword_text
        for sep in separators:
            normalized = normalized.replace(sep, ',')
        raw_tokens = [token.strip() for token in normalized.replace('\n', ',').split(',')]
        tokens = []
        for token in raw_tokens:
            if not token: continue
            for sub in token.split():
                sub = sub.strip()
                if sub: tokens.append(sub)
        return tokens

    def _is_economic_keyword(self, token: str) -> bool:
        for econ in self.ECON_KEYWORDS:
            if econ in token: return True
        return False

    def create_popup_html(self, db_region: str, stat: Dict, max_news: int = 5):
        news_list = self.loader.get_latest_news_by_region(db_region, limit=max_news)
        
        # 부정 비율에 따른 텍스트 강조 컬러
        ratio = stat['negative_ratio']
        if ratio > 51: status_color = "#f44336"
        elif ratio >= 50: status_color = "#999999"
        else: status_color = "#2196F3"

        html_content = f"""
        <div style="width: 700px; padding: 15px; font-family: 'Malgun Gothic', sans-serif; box-sizing: border-box;">
            <h3 style="margin-top: 0; margin-bottom: 10px; color: #fff; background: linear-gradient(135deg, #444 0%, #222 100%); 
                       padding: 12px 15px; border-radius: 5px; text-align: center;">
                📍 {db_region} 지역 뉴스
            </h3>
            
            <div style="background: #f8f9fa; padding: 12px; margin-bottom: 15px; border-radius: 5px; 
                        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center; border: 1px solid #ddd;">
                <div>
                    <div style="font-size: 0.8em; color: #666;">전체 뉴스</div>
                    <div style="font-size: 1.3em; color: #333; font-weight: bold;">{stat['count']}개</div>
                </div>
                <div>
                    <div style="font-size: 0.8em; color: #666;">부정 비율</div>
                    <div style="font-size: 1.3em; color: {status_color}; font-weight: bold;">{ratio:.1f}%</div>
                </div>
                <div>
                    <div style="font-size: 0.8em; color: #666;">부정 뉴스</div>
                    <div style="font-size: 1.3em; color: #f44336; font-weight: bold;">{stat['negative_count']}개</div>
                </div>
            </div>
            
            <div style="border-top: 2px solid #ddd; padding-top: 10px;">
                <h4 style="margin: 10px 0; color: #333; font-size: 0.95em;">📋 최신 뉴스 목록</h4>
                <div style="max-height: 350px; overflow-y: auto;">
        """
        
        for news in news_list:
            title = html.escape(news.get('title', '제목 없음'))
            url = news.get('url', '#')
            html_content += f"""
            <div style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #eee;">
                <a href="{url}" target="_blank" style="color: #1976D2; text-decoration: none; font-size: 0.9em;">• {title}</a>
            </div>
            """
        
        html_content += "</div></div></div>"
        return html_content

    def add_region_labels(self):
        for region, coord in REGION_COORDS.items():
            label_html = f"""<div style="font-size: 14px; font-weight: bold; color: black; text-shadow: 1px 1px 2px white;">{region}</div>"""
            folium.Marker(location=coord, icon=DivIcon(html=label_html), interactive=False).add_to(self.map)
    
    def add_geojson_layer(self, max_news: int = 10):
        if not self.geojson_data: return
        
        region_stats = self.get_region_statistics()
        EXCLUDED_REGIONS = ['Jeju', 'Dokdo', 'Ulleung-gun']
        
        for feature in self.geojson_data['features']:
            geojson_region = feature['properties'].get('NAME_1')
            if geojson_region in EXCLUDED_REGIONS: continue
            
            db_region = get_db_region(geojson_region)
            
            # --- 색상 결정 로직 ---
            if db_region and db_region in region_stats and region_stats[db_region]['count'] > 0:
                stat = region_stats[db_region]
                neg_ratio = stat['negative_ratio']
                
                if neg_ratio > 51:
                    fill_color = '#FF0000' # 부정 (빨강)
                elif neg_ratio < 50:
                    fill_color = '#0000FF' # 긍정 (파랑)
                else:
                    fill_color = '#FFFFFF' # 중립 (흰색)
                fill_opacity = 0.6
                popup_html = self.create_popup_html(db_region, stat, max_news)
            else:
                fill_color = '#CCCCCC' # 데이터 없음
                fill_opacity = 0.3
                popup_html = f"<div style='padding:10px;'><b>{geojson_region}</b><br>데이터가 없습니다.</div>"

            style_func = lambda x, fc=fill_color, fo=fill_opacity: {
                'fillColor': fc, 'fillOpacity': fo, 'color': '#333333', 'weight': 1.5
            }
            
            folium.GeoJson(
                feature,
                style_function=style_func,
                highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.8},
                popup=folium.Popup(IFrame(popup_html, width=730, height=500))
            ).add_to(self.map)
    
    def add_legend(self):
        legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; width: 220px; 
                    background: white; border: 2px solid #333; border-radius: 8px;
                    z-index: 9999; font-size: 13px; padding: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
            <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 14px;">🚩 부정 기사 비율 기준</p>
            <p style="margin: 5px 0;"><span style="background-color: #FF0000; width: 18px; height: 12px; display: inline-block; margin-right: 8px; border:1px solid #999;"></span>부정 위험 (51% 초과)</p>
            <p style="margin: 5px 0;"><span style="background-color: #FFFFFF; width: 18px; height: 12px; display: inline-block; margin-right: 8px; border:1px solid #999;"></span>중립 지역 (50% ~ 51%)</p>
            <p style="margin: 5px 0;"><span style="background-color: #0000FF; width: 18px; height: 12px; display: inline-block; margin-right: 8px; border:1px solid #999;"></span>긍정 우세 (50% 미만)</p>
            <p style="margin: 5px 0;"><span style="background-color: #CCCCCC; width: 18px; height: 12px; display: inline-block; margin-right: 8px; border:1px solid #999;"></span>데이터 부족</p>
        </div>
        '''
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def generate(self, output_file: str = 'news_map_geo.html', max_news: int = 10):
        self.load_geojson()
        self.create_map()
        self.add_geojson_layer(max_news=max_news)
        self.add_region_labels()
        self.add_legend()
        self.map.save(output_file)
        # 사이드 패널 로직은 기존과 동일하게 유지하거나 필요 시 위 필드명에 맞춰 수정하여 사용하세요.
        print(f"✅ 생성 완료: {os.path.abspath(output_file)}")

if __name__ == '__main__':
    generator = NewsMapGeneratorGeo()
    generator.generate('news_map_geo.html')