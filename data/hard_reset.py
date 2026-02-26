import sqlite3
import os

# DB_PATH = "data/news.db"  # DB 파일 경로

if not os.path.exists(DB_PATH):
    print(f"DB 파일이 존재하지 않습니다: {DB_PATH}")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # news 테이블 데이터 모두 삭제
    cursor.execute("DELETE FROM news;")
    conn.commit()

    # 필요 시 AUTOINCREMENT 초기화 (id 1부터 다시 시작)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='news';")
    conn.commit()

    conn.close()
    print("DB 전체 초기화 완료. 테이블 구조는 그대로 유지됩니다.")