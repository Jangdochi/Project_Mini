import sqlite3
import logging
import time
import analyzer.log_config as log_config
from analyzer.sentiment import NewsSentimentAnalyzer

logger = logging.getLogger(__name__)

DB_PATH = "data/news.db"


def run_analysis():
    start_time = time.time()
    logger.info("감성 배치 시작")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        #processed가 0인거 실행하기
        cursor.execute("""
            SELECT id, content
            FROM news
            WHERE is_processed = 0
        """)

        rows = cursor.fetchall()

        if not rows:
            logger.info("처리할 뉴스 없음")
            return

        analyzer = NewsSentimentAnalyzer()

        for news_id, content in rows:
            try:
                label, score = analyzer.predict(content)

                cursor.execute("""
                    UPDATE news
                    SET sentiment_score = ?,
                        is_processed = 1
                    WHERE id = ?
                """, (score, news_id))

                logger.info(
                    f"ID {news_id} 처리 완료 | 결과: {label} | 점수: {score:.4f}"
                )

            except Exception:
                logger.exception(f"ID {news_id} 처리 중 오류 발생")

        conn.commit()

    except Exception:
        logger.exception("배치 실행 중 치명적 오류 발생")

    finally:
        conn.close()
        elapsed = time.time() - start_time
        logger.info(f"감성 배치 종료 | 총 소요 시간: {elapsed:.2f}초")


if __name__ == "__main__":
    run_analysis()