# src/crawlers/crawler_manager.py

# 1. 경상도: busan_ilbo.py 파일 안의 GyeongsangCrawler 클래스
from src.crawlers.regional.gyeongsang.busan_ilbo import GyeongsangCrawler
# 2. 전라도: jeonnam_ilbo.py 파일 안의 JeollaCrawler 클래스 (스크린샷 확인됨)
from src.crawlers.regional.jeolla.jeonnam_ilbo import JeollaCrawler
# 3. 충청도: daejon_ilbo.py 파일 안의 ChungcheongCrawler 클래스
from src.crawlers.regional.chungcheong.daejon_ilbo import ChungcheongCrawler

class CrawlerManager:
    def __init__(self):
        self.crawlers = [
            GyeongsangCrawler(),
            JeollaCrawler(),
            ChungcheongCrawler()
        ]
    
    def run_all(self):
        for crawler in self.crawlers:
            print(f"{crawler.region_name} 크롤링 시작...")
            crawler.run()