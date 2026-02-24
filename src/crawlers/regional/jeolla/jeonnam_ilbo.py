import re
from src.crawlers.base_crawler import BaseCrawler

class JeollaCrawler(BaseCrawler):
    def __init__(self):
        # 지역명을 "전라도", 신문사명을 "전남일보"로 정확히 지정합니다.
        super().__init__("전라도", "전남일보")
        self.url = "https://www.jldnews.co.kr/news/articleList.html?sc_sub_section_code=S2N24&view_type=sm"
        self.domain = "https://www.jldnews.co.kr"
        
        # [중요] 저장 경로가 없으면 자동으로 생성하는 로직을 추가합니다.
        import os
        save_path = os.path.join("data", "raw_texts", "전라도", "전남일보")
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    def run(self):
        soup = self.get_soup(self.url)
        if not soup: return
        
        articles = soup.select(".altlist-webzine-item")
        print(f"    [전라도] 작업을 시작합니다...")
        print(f"    [전라도] 검색된 전체 기사: {len(articles)}개")

        for art in articles:
            try:
                # 1. 제목과 링크 추출 로직 보강
                # dt 내부에 제목이 있는 경우가 가장 많으므로 dt를 먼저 찾습니다.
                dt_tag = art.select_one("dt")
                a_tag = dt_tag.select_one("a") if dt_tag else art.select_one("a[href*='articleView']")
                
                if not a_tag: continue
                
                href = a_tag.get('href', '')
                if not href: continue
                
                # 2. [핵심] 제목 가져오기 (a태그 텍스트 -> dt 텍스트 -> img alt 순서로 시도)
                raw_title = a_tag.get_text().strip()
                if not raw_title and dt_tag:
                    raw_title = dt_tag.get_text().strip()
                if not raw_title:
                    img_tag = art.select_one("img")
                    raw_title = img_tag.get('alt', '').strip() if img_tag else "제목 없음"

                # 3. 파일명 정제 (특수문자 제거 및 길이 제한)
                clean_title = re.sub(r'[\n\r\t\\/:*?"<>|]', ' ', raw_title).strip()
                title = clean_title[:50] if clean_title else "제목 미확인"
                
                link = self.domain + href if href.startswith('/') else href
                
                # 분석 중인 제목을 터미널에 표시하여 확인합니다.
                print(f"    ▶ [기사 분석 중] {title[:30]}...") 
                
                detail_soup = self.get_soup(link)
                if not detail_soup: continue
                
                # 4. 본문 추출
                content_tag = detail_soup.select_one("#article-view-content-div")
                content = content_tag.get_text(separator="\n").strip() if content_tag else "본문 없음"
                
                full_content = f"{content}\n\n기사 원본 링크: {link}"
                
                # 5. 저장
                self.save_to_file(title, full_content)
                
            except Exception:
                continue