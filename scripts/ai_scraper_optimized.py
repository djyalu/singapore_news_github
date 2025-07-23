"""
AI 스크래핑 최적화 설정 및 유틸리티
"""

# 사이트별 우선순위와 기본 설정
SITE_PRIORITIES = {
    # High priority - 주요 뉴스 사이트
    "The Straits Times": {"priority": "high", "maxLinks": 5, "weight": 1.0},
    "Channel NewsAsia": {"priority": "high", "maxLinks": 5, "weight": 1.0},
    "The Business Times": {"priority": "high", "maxLinks": 4, "weight": 0.9},
    
    # Medium priority - 일반 뉴스 사이트
    "Yahoo Singapore News": {"priority": "medium", "maxLinks": 3, "weight": 0.7},
    "Mothership": {"priority": "medium", "maxLinks": 3, "weight": 0.7},
    "TODAY Online": {"priority": "medium", "maxLinks": 3, "weight": 0.7},
    "The New Paper": {"priority": "medium", "maxLinks": 3, "weight": 0.7},
    "AsiaOne": {"priority": "medium", "maxLinks": 3, "weight": 0.6},
    "MustShareNews": {"priority": "medium", "maxLinks": 3, "weight": 0.6},
    
    # Low priority - 특수 목적 사이트
    "The Independent Singapore": {"priority": "low", "maxLinks": 2, "weight": 0.5},
    "Tech in Asia": {"priority": "low", "maxLinks": 2, "weight": 0.5},
    "The Edge Singapore": {"priority": "low", "maxLinks": 2, "weight": 0.5},
    "Lianhe Zaobao": {"priority": "low", "maxLinks": 2, "weight": 0.4},
    "Singapore Business Review": {"priority": "low", "maxLinks": 2, "weight": 0.4},
    "Coconuts Singapore": {"priority": "low", "maxLinks": 2, "weight": 0.3},
    "Time Out Singapore": {"priority": "low", "maxLinks": 2, "weight": 0.3}
}

def get_optimized_site_config(site_name, default_priority="medium"):
    """사이트별 최적화된 설정 반환"""
    return SITE_PRIORITIES.get(site_name, {
        "priority": default_priority,
        "maxLinks": 3,
        "weight": 0.5
    })

def calculate_api_budget(total_sites, max_api_calls=100):
    """API 호출 예산 계산"""
    # 우선순위별 사이트 수 계산
    priority_counts = {"high": 0, "medium": 0, "low": 0}
    total_weight = 0
    
    for site_name, config in SITE_PRIORITIES.items():
        priority = config["priority"]
        priority_counts[priority] += 1
        total_weight += config["weight"]
    
    # 우선순위별 API 예산 배분
    api_budget = {
        "high": int(max_api_calls * 0.5),    # 50%
        "medium": int(max_api_calls * 0.35),  # 35%
        "low": int(max_api_calls * 0.15)      # 15%
    }
    
    return api_budget

def get_dynamic_link_limit(site_name, remaining_api_calls, sites_remaining):
    """남은 API 호출 수에 따라 동적으로 링크 수 조정"""
    config = get_optimized_site_config(site_name)
    base_limit = config["maxLinks"]
    
    # API 호출이 부족하면 링크 수 감소
    if remaining_api_calls < 20:
        return max(1, base_limit // 2)
    elif remaining_api_calls < 50:
        return max(2, base_limit - 1)
    else:
        return base_limit

# AI 스크래핑 최적화 전략
OPTIMIZATION_STRATEGIES = {
    "aggressive": {
        "max_api_calls": 100,
        "cache_ttl": 3600,  # 1시간 캐시
        "batch_size": 5,
        "skip_low_priority": True
    },
    "balanced": {
        "max_api_calls": 150,
        "cache_ttl": 1800,  # 30분 캐시
        "batch_size": 3,
        "skip_low_priority": False
    },
    "conservative": {
        "max_api_calls": 200,
        "cache_ttl": 900,   # 15분 캐시
        "batch_size": 2,
        "skip_low_priority": False
    }
}

def get_optimization_strategy(mode="balanced"):
    """최적화 전략 반환"""
    return OPTIMIZATION_STRATEGIES.get(mode, OPTIMIZATION_STRATEGIES["balanced"])