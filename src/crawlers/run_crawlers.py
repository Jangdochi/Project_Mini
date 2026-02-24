# src/crawlers/run_crawlers.py
from src.crawlers.regional.gyeongsang.busan_ilbo import GyeongsangCrawler
from src.crawlers.regional.jeolla.jeonnam_ilbo import JeollaCrawler
from src.crawlers.regional.chungcheong.daejon_ilbo import ChungcheongCrawler

def main():
    print("=== 크롤링 프로세스 시작 ===")
    
    # 1. 경상도 직접 실행
    print("1. 경상도 작업을 시작합니다...")
    gs = GyeongsangCrawler()
    gs.run()
    
    # 2. 전라도 직접 실행
    print("\n2. 전라도 작업을 시작합니다...")
    jn = JeollaCrawler()
    jn.run()
    
    # 3. 충청도 직접 실행
    print("\n3. 충청도 작업을 시작합니다...")
    cc = ChungcheongCrawler()
    cc.run()

    print("\n=== 모든 작업 완료 ===")

if __name__ == "__main__":
    main()