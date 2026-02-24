import re
from src.crawlers.base_crawler import BaseCrawler

class GyeongsangCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("경상도", "경상뉴스")
        self.url = "http://m.ynews.kr/list.php?part_idx=300"
        self.domain = "http://m.ynews.kr"

    def run(self):
        soup = self.get_soup(self.url)
        if not soup: return
        
        # 기사 목록 영역 선택
        articles = soup.select(".list_type1 li")
        print(f"    [경상도] 검색된 전체 기사: {len(articles)}개")

        for art in articles:
            try:
                a_tag = art.select_one("a")
                if not a_tag: continue
                
                link_url = a_tag.get('href', '')
                if "view.php" not in link_url: continue
                
                # 1. 제목 정제 (정규표현식을 사용하여 더 안전하게 처리)
                raw_title = a_tag.get_text().strip()
                clean_title = re.sub(r'[\n\r\t\\/:*?"<>|]', ' ', raw_title).strip()
                title = clean_title[:50] 
                
                # 2. 상세 페이지 링크 생성
                link = self.domain + "/" + link_url.lstrip('/')
                detail_soup = self.get_soup(link)
                if not detail_soup: continue
                
                # 3. [최종 해결] 경상뉴스 모바일 본문 추출 무적 로직
                # 개발자 도구 분석 결과 ID와 Class가 혼용될 수 있으므로 둘 다 체크합니다.
                content_tag = detail_soup.select_one("#view_con") or \
                              detail_soup.select_one(".view_con") or \
                              detail_soup.select_one("#contents .view_con") or \
                              detail_soup.select_one(".article_content")
                
                # 4. 본문 내용 추출 및 정밀 정제
                if content_tag:
                    # 불필요한 스크립트, 광고, 버튼 등 제거 (추출 퀄리티 향상)
                    for s in content_tag(["script", "style", "button", "ins"]):
                        s.decompose()
                    content = content_tag.get_text(separator="\n").strip()
                else:
                    # 위 태그들이 다 실패할 경우를 대비한 최후의 수단
                    all_text = detail_soup.select_one("#contents")
                    content = all_text.get_text(separator="\n").strip() if all_text else "본문을 찾을 수 없습니다."
                
                full_content = f"{content}\n\n기사 원본 링크: {link}"
                
                # 5. 파일 저장 및 진행 상황 출력
                print(f"    ▶ [경상도 파일 생성 완료] {title[:20]}...")
                self.save_to_file(title, full_content)
                
            except Exception as e:
                print(f"    [경상도] 개별 기사 저장 중 에러: {e}")
                continue