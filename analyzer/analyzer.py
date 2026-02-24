from pathlib import Path
import logging
import time
import analyzer.log_config as log_config
from analyzer.sentiment import NewsSentimentAnalyzer
from pathlib import Path

logger = logging.getLogger(__name__)

def run_analysis():
    start_time = time.time()
    try:
        BASE_DIR = Path(__file__).resolve().parent.parent
        file_path = BASE_DIR / "analyzer/data" / "example1.txt"
        logger.info("프로그램 시작")

        if not file_path.exists():
            logger.warning(f"파일을 찾을 수 없음: {file_path}")
            return

        logger.info(f"파일 분석 시작: {file_path.name}")
        analyzer = NewsSentimentAnalyzer()

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        sentiment, score = analyzer.predict(text)
        logger.info(f"분석 완료 | 결과: {sentiment} | 점수: {score:.4f}")

    except Exception:
        logger.exception("실행부에서 치명적 오류 발생")

    finally:
        elapsed = time.time() - start_time
        logger.info(f"프로그램 종료 | 총 소요 시간: {elapsed:.2f}초")


if __name__ == "__main__":
    run_analysis()