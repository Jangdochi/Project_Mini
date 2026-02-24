# Regional News Crawler Project

Python web crawler project for collecting economic news from regional newspapers (Seoul, Gyeonggi-do, Gangwon-do).

## Project Structure
```
src/
├── crawlers/
│   ├── base_crawler.py       # Base crawler class
│   ├── regional/
│   │   ├── seoul/
│   │   │   └── seoul_shinmun.py
│   │   ├── gyeonggi/
│   │   │   └── gyeonggi_ilbo.py
│   │   └── gangwon/
│   │       └── gangwon_domin_ilbo.py
│   ├── crawler_manager.py
│   └── run_crawlers.py
└── data/
    └── regional_news.csv
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
# Run all crawlers
python src/crawlers/run_crawlers.py --mode all --articles 50

# Run specific region
python src/crawlers/run_crawlers.py --mode region --region 서울 --articles 30
```

## Development
- Base crawler class with abstract methods
- Regional newspaper crawlers extending base class
- Error handling and logging
- CSV output format
