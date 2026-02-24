import os
import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import time     # 지연 시간 추가
import random   # 랜덤 값 생성 추가

class BaseCrawler:
    def __init__(self, region_name, folder_name):
        self.region_name = region_name
        self.press_name = folder_name
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.save_dir = os.path.join(self.base_dir, "data", "raw_texts", region_name, folder_name)
        self.db_path = os.path.join(self.base_dir, "news_database.db")
        
        # [차단방지] 다양한 브라우저 헤더 리스트
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/121.0.0.0'
        ]

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
            
        self._init_db()

    def _init_db(self):
        """데이터베이스 및 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT,
                press TEXT,
                title TEXT,
                content TEXT,
                link TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_soup(self, url):
        """차단 방지 로직이 강화된 soup 객체 반환"""
        # [차단방지 1] 무작위 대기 (1.5초 ~ 3.5초 사이)
        # 너무 일정한 간격은 봇으로 간주됩니다.
        time.sleep(random.uniform(1.5, 3.5))

        # [차단방지 2] 헤더 다양화 및 세션 사용
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.google.com/' # 구글 검색을 통해 들어온 것처럼 위장
        }

        try:
            # 단순 requests.get 대신 Session을 쓰면 쿠키 관리가 되어 더 안전
            with requests.Session() as session:
                res = session.get(url, headers=headers, timeout=15)
                
                # 상태 코드 확인 (200이 아니면 차단 또는 페이지 부재)
                if res.status_code == 200:
                    res.encoding = 'utf-8'
                    return BeautifulSoup(res.text, 'html.parser')
                elif res.status_code == 404:
                    print(f"      [404 에러] 페이지가 존재하지 않음: {url}")
                elif res.status_code == 403:
                    print(f"      [403 에러] 접근 차단됨(Forbidden). 대기 시간을 늘리세요.")
                else:
                    print(f"      [에러] 상태 코드 {res.status_code}: {url}")
                return None

        except Exception as e:
            print(f"      [예외 발생] 접속 실패: {e}")
            return None

    def save_to_file(self, title, content):
        """텍스트 파일 저장 및 DB 저장 호출"""
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()[:50]
        if not safe_title: safe_title = "no_title"
        
        file_path = os.path.join(self.save_dir, f"{safe_title}.txt")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      ▶ [파일 완료] {safe_title}")
            
            # 링크 추출 로직
            link = "링크 정보 없음"
            if "기사 원본 링크: " in content:
                link = content.split("기사 원본 링크: ")[-1].strip()
            
            self.save_to_db(title, content, link)
        except Exception as e:
            print(f"      [파일 저장 에러] {e}")

    def save_to_db(self, title, content, link):
        """SQLite DB에 기사 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO news (region, press, title, content, link) VALUES (?, ?, ?, ?, ?)",
                (self.region_name, self.press_name, title, content, link)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"      [DB 에러] {e}")