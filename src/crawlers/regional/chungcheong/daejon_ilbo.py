from src.crawlers.base_crawler import BaseCrawler

class ChungcheongCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("충청도", "충청뉴스")
        self.url = "http://www.ccnnews.co.kr/news/articleList.html?sc_section_code=S1N3&view_type=sm"

    def run(self):
        soup = self.get_soup(self.url)
        # 이미지 bb62f5 기준 리스트 블록
        articles = soup.select("div.list-block")
        print(f"    [충청도] 검색된 전체 기사: {len(articles)}개")

        for art in articles:
            try:
                title_tag = art.select_one(".list-titles a")
                if not title_tag: continue
                
                title = title_tag.text.strip()
                link = "http://www.ccnnews.co.kr" + title_tag['href']

                detail_soup = self.get_soup(link)
                content_tag = detail_soup.select_one("#article-view-content-div")
                content = content_tag.get_text(separator="\n").strip() if content_tag else "본문 없음"

                full_content = f"{content}\n\n기사 원본 링크: {link}"
                self.save_to_file(title, full_content)
            except Exception as e:
                print(f"    [충청도] 오류 발생: {e}")