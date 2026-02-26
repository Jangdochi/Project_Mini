"""
지역 좌표 정의
한국 주요 지역의 위도, 경도 좌표
"""

from typing import Dict, Tuple


# 지역별 중심 좌표 (위도, 경도)
REGION_COORDS: Dict[str, Tuple[float, float]] = {
    '서울': (37.565, 127.380),    # 서울(더 안쪽, 시청~종로 부근)
    '경기도': (37.25, 127.35),    # 경기도(더 아래, 더 오른쪽)
    '강원도': (37.80, 128.35),    # 강원도(오른쪽으로)
    '충청도': (36.70, 127.70),    # 충청도(중앙)
    '경상도': (36.30, 128.90),    # 경상도(오른쪽으로)
    '전라도': (35.50, 127.45),    # 전라도(오른쪽으로)
}

# 한국 중심 좌표 (전체 지도 표시 시 사용)
KOREA_CENTER = (36.5, 127.5)

# 기본 줌 레벨
DEFAULT_ZOOM = 7

# 지역별 줌 레벨 (지역 클릭 시)
REGION_ZOOM = 10


def get_region_coord(region: str) -> Tuple[float, float]:
    """
    지역 좌표 가져오기
    
    Args:
        region: 지역명
    
    Returns:
        (위도, 경도) 튜플
    """
    return REGION_COORDS.get(region, KOREA_CENTER)


def get_all_regions() -> list:
    """
    모든 지역 이름 리스트 반환
    
    Returns:
        지역명 리스트
    """
    return list(REGION_COORDS.keys())


if __name__ == '__main__':
    # 테스트
    print("=== 지역별 좌표 ===")
    for region, coord in REGION_COORDS.items():
        print(f"{region}: {coord}")
    
    print(f"\n한국 중심: {KOREA_CENTER}")
    print(f"기본 줌: {DEFAULT_ZOOM}")
