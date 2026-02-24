# 📑 Data_Collection_PRD.md: 지능형 지역 경제 모니터링 데이터 수집 가이드
**EcoMap Insight: Macro-Micro Economic Sentiment Analysis**

## 1. 개요 (Introduction)
- **제품명**: **EcoMap Insight**
- **수집 원칙**: 자산 가격 변동성 분석을 위해 모든 뉴스 데이터는 발행일 기준 **일 단위(Daily)**로 수집하며, 날짜 형식은 `YYYY-MM-DD`로 강제 정규화함.
- **제품 비전**: 전국 거시 지표와 지역 미시 여론을 결합하여 자산 가격(주식, 부동산) 변동과의 상관관계($r$)를 시각화하고 증명함.

---

## 2. 데이터 관리 및 저장 전략 (Storage Strategy)

### 2.1. 프로젝트 폴더 구조
- **`data_collection/`**: 파이썬 수집 스크립트 및 공통 모듈 저장소.
- **`data/`**: 수집된 개별 언론사 CSV 파일 저장소 (`raw_{region}_{press}.csv`).
- **`logs/`**: 실행 시간별 로그 데이터 저장소 (`{name}_{timestamp}.log`).

### 2.2. 단계별 저장 구조 (이원화 전략)
1. **Raw Layer (Individual CSV)**: 
   - **방식**: 각 수집 담당자가 맡은 권역/언론사별로 개별 CSV 파일을 생성.
   - **데이터**: 기사 제목, 요약, **본문 전체(content)**, 이미지 URL, 원문 링크 등 전체 메타데이터 보존.
2. **Processed Layer (Unified SQLite DB)**:
   - **방식**: 데이터 엔지니어가 개별 CSV를 읽어 하나의 DB 테이블에 통합 적재.

### 2.3. 수집 주기 및 범위
- **수집 주기**: **일 단위(Daily)** (매일 오전 전일 데이터 업데이트).
- **수집 기간**: **2025-02-23 ~ 2026-02-23** (초기 구축 데이터 범위).
- **페이지네이션 제한**: 서버 부하 및 안정성을 위해 스크래퍼당 **최대 500페이지**로 제한.

### 2.4. 통합 데이터 스키마 (Unified Data Schema)
모든 언론사별 CSV(`raw_{region}_{press}.csv`)는 아래의 컬럼명과 순서를 엄격히 준수한다.
1. `date`: 발행일 (`YYYY-MM-DD`)
2. `press`: 언론사명 (예: 매일경제, 서울신문)
3. `region`: 수집 권역 (national, seoul, gyeonggi, incheon, chungcheong)
4. `title`: 기사 제목
5. `sub_title`: 기사 부제목 또는 상세 페이지 내 강조 문구 (없을 경우 빈 문자열)
6. `description`: 목록 페이지의 짧은 요약 (또는 기사 서두) (없을 경우 빈 문자열)
7. `content`: 상세 페이지 내 기사 본문 전체 (광고/스크립트 제거)
8. `article_url`: 기사 원문 링크
9. `image_url`: 대표 이미지 주소 (없을 경우 빈 문자열)

---

## 3. 권역별 수집 상세 사양

### [A조] 수도권 및 중부권

#### 3.1. 전국 (한국경제)
- **Target URL**: 
  - [https://www.hankyung.com/economy/economic-policy](https://www.hankyung.com/economy/economic-policy) (경제정책)
  - [https://www.hankyung.com/economy/macro](https://www.hankyung.com/economy/macro) (거시경제)
  - [https://www.hankyung.com/economy/forex](https://www.hankyung.com/economy/forex) (외환/금융)
  - [https://www.hankyung.com/economy/tax](https://www.hankyung.com/economy/tax) (세제/부동산)
  - [https://www.hankyung.com/economy/job-welfare](https://www.hankyung.com/economy/job-welfare) (고용복지)
- **Selectors (목록 페이지)**: 
  - `Item Container`: `ul.news-list > li` 
  - `Title`: `h2.news-tit`
  - `Description`: `p.lead` (목록 페이지 기사 요약본)
  - `Date`: `p.txt-date` (추출 예시: `2026.02.22 17:17` → 정규화: `YYYY-MM-DD`)
  - `Article_URL`: `h2.news-tit a` (href 속성)
  - `Image_URL`: `figure.thumb img` (src 속성)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: 
    - `Location`: 뉴스 상세 페이지 내부 제목 상단/하단
    - `Selector`: `strong.subTitle_s2` (또는 `h2.sub_title`)
  - **[추가] Content**: 
    - `Location`: 뉴스 상세 페이지 내부 본문 영역
    - `Selector`: `div#articletxt`
    - `Extraction Logic`: `div#articletxt` 내부 텍스트를 추출하되, `utils.py`의 `clean_text` 로직을 통해 내부 광고, 이미지 캡션(`figcaption`), 관련 뉴스 링크, 저작권 공지 문구를 자동 제거함.

#### 3.2. 서울 (서울신문)
- **Target URL**: [https://seoul.co.kr/newsList/economy](https://seoul.co.kr/newsList/economy)
- **Selectors (목록)**: 
  - `Item`: `li.newsBox_row1` 
  - `Title`: `h2.h28` / `Link`: `div.articleTitle a`
  - `Date`: `div.ArticleInfo span.body14` (정규화: `YYYY-MM-DD`)
- **Selectors (상세 페이지)**:
  - **[NEW] Sub Title**: `strong.subTitle_s2` (기사 상단 강조 문구 및 소제목)
  - **[NEW] Content**: 
    - `Selector`: `div#articleContent`
    - `Extraction Logic`: `div.viewContent` 내부 텍스트를 추출하되, 하단 `div.quizContainer`(AI 퀴즈), 광고(`ins`, `script`), 저작권 문구(`div.articleCopyright`)를 제외한 순수 기사 본문만 결합.

#### 3.3. 경기 (경인일보)
- **Target URL**: [https://www.kyeongin.com/money](https://www.kyeongin.com/money)
- **Selectors (목록)**: 
  - `Item`: `ul.list-type01 li` (또는 메인 섹션의 `div.box`)
  - `Title`: `h4.title` / `Link`: `a`
  - `Date`: 상세 페이지 접속 후 추출 권장 (목록에 날짜가 없을 경우 대비)
- **Selectors (상세 페이지)**:
  - **[NEW] Sub Title**: `div.article-mtitle` 내부의 모든 `p` 태그 텍스트 결합
  - **[NEW] Content**: 
    - `Selector`: `div.article-body`
    - `Extraction Logic`: 내부의 광고(`iframe`), 이미지 캡션(`figcaption`), 저작권 문구(`.copyright`), 관련 기사(`div.article-photo-wrap`) 등을 제외한 순수 기사 텍스트 추출.

#### 3.4. 인천 (인천일보)
- **Target URL**: [https://www.incheonilbo.com/news/articleList.html?sc_section_code=S1N4&view_type=sm](https://www.incheonilbo.com/news/articleList.html?sc_section_code=S1N4&view_type=sm)
- **Selectors (목록)**: 
  - `Item`: `div.list-block`, `ul.type2 li`
  - `Title`: `div.titles a`, `h4.titles a` / `Link`: `href` 속성
  - `Date`: `div.info-group span.date`, `em.datetime`
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `h2.subheading` (기사 요약 및 핵심 소제목)
  - **[추가] Content**: 
    - `Selector`: `div#article-view-content-div`
    - `Extraction Logic`: 내부의 광고(`iframe`, `div.ad-template`), 이미지 설명(`figcaption`), 기자 메일 정보(`.byline`), 저작권 공지(`.article-copy`) 등을 제외한 순수 기사 본문 텍스트 추출.

#### 3.5. 충청/대전 (충청투데이)
- **Target URL**: [https://www.cctoday.co.kr/news/articleList.html?sc_section_code=S1N4&view_type=sm](https://www.cctoday.co.kr/news/articleList.html?sc_section_code=S1N4&view_type=sm)
- **Selectors (목록)**: 
  - `Item`: `div.list-block`, `section.type2 li`
  - `Title`: `div.titles a` / `Link`: `href` 속성
  - `Date`: `div.info-group span.date` (또는 상세 페이지 추출)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `h4.subheading` (기사 요약 및 소제목)
  - **[추가] Content**: 
    - `Selector`: `div#article-view-content-div`
    - `Extraction Logic`: 내부 광고(`iframe`, `div.banner_box`), 이미지 설명(`figcaption`), 기자 정보(`.account`), 저작권(`.article-copy`), 관련 기사(`.relation`) 요소를 모두 제거한 순수 본문 텍스트.

---

### [B조] 남부권 및 강원/제주/데이터 플랫폼

#### 3.6. [B조] 수집 개요
- 남부권 제조 벨트와 강원/제주 관광 및 부동산 특화 데이터를 중심으로 수집한다.

#### 3.7. 부산/경남 (부산일보)
- **Target URL**: [https://www.busan.com/newsList/busan/0201000000](https://www.busan.com/newsList/busan/0201000000) (경제해양 섹션)
- **수집 목표**: 해운, 조선, 가덕도 신공항 등 동남권 메가시티 및 남부권 경제 핵심 이슈 수집 및 지역 여론 감성 분석.
- **Selectors (목록 페이지)**: 
  - `Item Container`: `ul#article_list li` 
  - `Title`: `p.title a`
  - `Description`: `p.body a` (목록에서 제공하는 기사 서두 요약 텍스트)
  - `Date`: `p.date` (추출 예시: `2026-02-23 [20:58]`)
    - *정규화 로직*: `[` 문자 기준 앞부분만 split 하거나, `YYYY-MM-DD` 정규표현식으로 정제하여 저장.
  - `Article_URL`: `p.title a` (href 속성)
    - *주소 보정*: 상대 경로(`/view/...`)로 추출되므로 `https://www.busan.com` 도메인과 결합 필수.
  - `Image_URL`: `div.thumb img` (src 속성)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `div.sub_title` (또는 존재할 경우 `h3.read_sub_tit`)
  - **[추가] Content**: 
    - `Selector`: `div#article-view-content-div`
    - `Extraction Logic`:
      - **제거 대상**: 내부 광고(`div.wcms_ad`), 이미지 캡션(`figcaption`), 관련 기사 추천 영역, 하단 기자 이메일 정보.
      - **정제**: `clean_text` 함수를 통해 저작권 문구 및 무단 전재 금지 텍스트 필터링 후 순수 본문만 저장.
- **페이지네이션**: `?page={n}` 쿼리 스트링 방식을 사용하여 1~500페이지까지 순차 수집.

#### 3.8. 경남 (경남경제)
- **Target URL**: [https://www.gnen.net/news/articleList.html?sc_section_code=S1N2&view_type=sm](https://www.gnen.net/news/articleList.html?sc_section_code=S1N2&view_type=sm) (경제 섹션)
- **수집 목표**: 경남 지역 투자 유치(MOU), 원자력/방산/우주항공 등 전략 산업 동향 및 소상공인 지원책 수집.
- **Selectors (목록 페이지)**: 
  - `Item Container`: `section#section-list ul.type > li` 
  - `Title`: `h4.titles a`
  - `Description`: `p.lead a` (웹진형 목록에서 제공하는 요약 텍스트)
  - `Date`: `span.byline em.date` (추출 예시: `2026.02.23 17:13`)
    - *정규화 로직*: `common_parse_date`를 통해 `YYYY-MM-DD` 형식으로 변환.
  - `Article_URL`: `h4.titles a` (href 속성)
    - *주소 보정*: 상대 경로로 추출되므로 `https://www.gnen.net` 도메인과 결합 필수.
  - `Image_URL`: `a.thumb img` (src 속성)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `h3.sub-titles` (또는 `div.sub-title`)
  - **[추가] Content**: 
    - `Selector`: `div#article-view-content-div`
    - `Extraction Logic`:
      - **제거 대상**: 광고(`div.ad-area`), 관련기사 링크, 하단 기자 바이라인, `figure` 내 캡션 정보.
      - **정제**: `clean_text` 함수를 사용하여 불필요한 줄바꿈 및 특수문자 제거 후 저장.
- **페이지네이션**: `&page={n}` 쿼리 스트링 방식을 사용하여 수집 목표 기간 도달 시까지 순차 수집.

#### 3.9. 대구/경북 (매일신문)
- **Target URL**: [https://www.imaeil.com/economy](https://www.imaeil.com/economy)
- **수집 목표**: 자동차 부품, 섬유 등 대구·경북 전통 제조 산업 및 TK 통합특별시, 대구경북 신공항 등 지역 경제 모멘텀 데이터 수집.
- **Selectors (목록 페이지)**: 
  - `Item Container`: `div.hdl_002 li`, `div.arl_018 li` (헤드라인과 일반 목록 병행 추출)
  - `Title`: `p.title a`
  - `Description`: `p.body` (목록에서 제공하는 기사 요약 텍스트)
  - `Date`: `p.date` (추출 예시: `2026-02-23 20:39:42`)
    - *정규화 로직*: `common_parse_date`를 활용하여 `YYYY-MM-DD` 형식으로 변환.
  - `Article_URL`: `p.title a` (href 속성)
  - `Image_URL`: `div.thumb img` (src 속성)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `div.sub_title` 또는 `p.sub_title` (상세 페이지 내 부제 영역)
  - **[추가] Content**: 
    - `Selector`: `div.article_content` (또는 `div.news_cnt`)
    - `Extraction Logic`:
      - **제거 대상**: 광고 이미지 및 스크립트, `div.wcms_ad`, 하단 기자 정보 섹션, 이미지 캡션.
      - **정제**: `clean_text` 함수를 적용하여 불필요한 공백과 저작권 문구를 필터링한 후 본문 데이터 결합.
- **페이지네이션**: `https://www.imaeil.com/economy?page={n}` 쿼리 스트링 구조를 활용하여 최대 500페이지까지 순차 수집.

#### 3.10. 광주/전라 (광주일보)
- **Target URL**: [http://www.kwangju.co.kr/section.php?sid=5](http://www.kwangju.co.kr/section.php?sid=5) (경제 섹션)
- **수집 목표**: 태양광·에너지 밸리, 모빌리티, 지역 건설 경기 등 호남권 신산업 및 실물 경제 동향 데이터 수집.
- **Selectors (목록 페이지)**: 
  - `Item Container`: `ul.section_list li` (헤드라인 `li.section_head` 포함)
  - `Title`: `div` (또는 `li > a > div` 텍스트)
  - `Description`: `p` (목록에서 제공하는 기사 요약 텍스트)
  - `Date`: `span.newsdate` (추출 예시: `2026.02.23 16:30`)
    - *정규화 로직*: `common_parse_date`를 통해 `YYYY-MM-DD` 형식으로 정규화.
  - `Article_URL`: `a` (href 속성)
    - *주소 보정*: 상대 경로(`/article.php?aid=...`)로 추출되므로 도메인(`http://www.kwangju.co.kr`) 결합 필수.
  - `Image_URL`: `span.thumb img` (src 속성)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `div.article_subtitle` (상세 페이지 내 부제 영역 존재 시 추출)
  - **[추가] Content**: 
    - `Selector`: `div#articleBody` (또는 `div.article_content`)
    - `Extraction Logic`:
      - **제거 대상**: 광고 스크립트, 하단 기자명 및 이메일 정보, 저작권 문구, 이미지 캡션.
      - **정제**: `clean_text` 함수를 통해 불필요한 태그와 공백을 제거한 후 순수 본문 텍스트만 추출.
- **페이지네이션**: `http://www.kwangju.co.kr/section.php?sid=5&page={n}` 쿼리 스트링 구조를 활용하여 최대 500페이지까지 순차 수집.

#### 3.11. 강원 (강원일보)
- **Target URL**: [https://www.kwnews.co.kr/economy/all](https://www.kwnews.co.kr/economy/all)
- **수집 전략 (한 달 단위)**: 
  - URL 파라미터 `?page={page}`를 활용하여 페이지네이션 수행.
  - 목록의 기사 날짜가 `2026-02-01` 미만으로 내려가면 수집 중단.
- **Selectors (목록)**: 
  - `Item`: `div.arl_023 > ul > li`
  - `Title`: `p.title a`
  - `Date`: `p.date` (형식: `YYYY-MM-DD HH:MM:SS`) -> `YYYY-MM-DD`로 정규화
  - `Summary`: `p.body a`
- **Selectors (상세 페이지)**:
  - **[추가] Content**: 
    - `Selector`: `div#articleBody` (또는 본문 텍스트 영역)
    - `Extraction Logic`: 기사 전문을 추출하되, 하단 기자 이메일 정보와 저작권 문구(`Copyright ⓒ...`)를 제외.

#### 3.12. 제주 (제주일보)
- **Target URL**: [http://www.jejunews.com/news/articleList.html?sc_section_code=S1N5&view_type=sm](http://www.jejunews.com/news/articleList.html?sc_section_code=S1N5&view_type=sm)
- **Selectors (목록)**: 
  - `Item`: `div.list-block`
  - `Title`: `div.list-titles a` / `Date`: `div.list-dated` (정규화 필수)
- **Selectors (상세 페이지)**:
  - **[추가] Sub Title**: `div.user-snb h2`, `div.article-head-title` (기사 요약 및 부제)
  - **[추가] Content**: 
    - `Selector`: `article#article-view-content-div`
    - `Extraction Logic`: `figcaption`(이미지 설명), `script`, `iframe`, 광고 배너, 하단 기자 정보를 제외한 순수 본문 텍스트.

#### 3.13. 뉴스 빅데이터 (빅카인즈)
- **Target URL**: [https://www.bigkinds.or.kr](https://www.bigkinds.or.kr)
- **수집 전략**: 
  - 특정 키워드(예: "금리", "부동산") 검색 결과의 **엑셀 다운로드** 기능 활용 또는 API 연동.
  - 개별 기사 본문보다는 **연관어 분석 데이터(키워드 네트워크)** 수집 중심.
- **수집 항목**: 키워드 빈도수, 가중치 점수, 언론사별 보도 비중.

---

## 4. 기술 고려사항 (Technical Checklist)

- **공통 모듈 (`utils.py`)**: 
  - HTTP 요청, 재시도 로직, 날짜 정규화, 본문 추출, CSV 저장을 공통 함수로 관리.
- **날짜 정규화**: 상대 시간(분 전, 시간 전) 및 다양한 점(`.`) 구분 형식을 `YYYY-MM-DD`로 자동 변환.
- **본문 수집**: 상세 페이지(`article_url`)에 자동 접속하여 기사 전체 텍스트 수집. 광고 및 스크립트 태그 자동 제거.
- **안정성 강화 (Retry)**: 네트워크 연결 오류 또는 서버 차단(`RemoteDisconnected`) 발생 시 **최대 3회 재시도** 루프 가동. 실패 시 점진적 대기 시간 증가.
- **한글 깨짐 방지**: `response.apparent_encoding` 자동 감지 및 CSV 저장 시 `utf-8-sig` 인코딩 적용.
- **파일 보호**: `PermissionError` 예외 처리를 통해 CSV 파일이 열려 있을 경우 사용자에게 알림 제공.
