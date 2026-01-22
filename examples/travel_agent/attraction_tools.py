"""
旅行助手 - 景点推荐工具

提供旅游景点推荐功能，基于天气和城市进行智能推荐
"""

from typing import Dict, List


# 模拟的景点数据库（实际应用中可以使用真实 API 或数据库）
ATTRACTIONS_DB: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "北京": {
        "晴天": [
            {"name": "颐和园", "desc": "美丽的皇家园林，可以泛舟昆明湖，欣赏湖景和古建筑", "indoor": False},
            {"name": "八达岭长城", "desc": "壮观的世界文化遗产，体验'不到长城非好汉'的豪迈", "indoor": False},
            {"name": "天坛公园", "desc": "明清两代皇帝祭祀上天的场所，建筑宏伟，环境优美", "indoor": False},
        ],
        "多云": [
            {"name": "故宫博物院", "desc": "中国最大的古代文化艺术博物馆，明清两代的皇家宫殿", "indoor": False},
            {"name": "天安门广场", "desc": "世界上最大的城市中心广场，见证中国历史的重要地点", "indoor": False},
        ],
        "雨天": [
            {"name": "中国国家博物馆", "desc": "收藏中华文明历史文物的最高殿堂，室内参观不受天气影响", "indoor": True},
            {"name": "首都博物馆", "desc": "了解北京历史文化的好去处，丰富的馆藏令人叹为观止", "indoor": True},
            {"name": "798艺术区", "desc": "充满创意的艺术园区，各种画廊和咖啡馆适合雨天闲逛", "indoor": True},
        ]
    },
    "上海": {
        "晴天": [
            {"name": "外滩", "desc": "上海的标志性景点，欣赏黄浦江两岸风光和万国建筑博览群", "indoor": False},
            {"name": "东方明珠塔", "desc": "上海地标建筑，登塔俯瞰整个上海滩的繁华景色", "indoor": False},
        ],
        "多云": [
            {"name": "豫园", "desc": "明代私家园林，体验传统江南园林之美", "indoor": False},
            {"name": "南京路步行街", "desc": "中华商业第一街，购物和美食的天堂", "indoor": False},
        ],
        "雨天": [
            {"name": "上海博物馆", "desc": "中国古代艺术博物馆，青铜器、陶瓷、书画等馆藏丰富", "indoor": True},
            {"name": "上海科技馆", "desc": "集科技、教育、娱乐于一体的大型科普场馆", "indoor": True},
        ]
    },
    "杭州": {
        "晴天": [
            {"name": "西湖", "desc": "'人间天堂'的精华所在，断桥残雪、苏堤春晓等十景闻名天下", "indoor": False},
            {"name": "灵隐寺", "desc": "千年古刹，佛教文化圣地，环境清幽", "indoor": False},
        ],
        "多云": [
            {"name": "西溪湿地", "desc": "城市中的天然氧吧，体验湿地生态之美", "indoor": False},
            {"name": "雷峰塔", "desc": "西湖十景之一'雷峰夕照'所在地，登塔远眺西湖全景", "indoor": False},
        ],
        "雨天": [
            {"name": "中国丝绸博物馆", "desc": "世界上最大的丝绸博物馆，了解丝绸文化历史", "indoor": True},
            {"name": "浙江博物馆", "desc": "展示浙江地区历史文化和自然风貌的综合博物馆", "indoor": True},
        ]
    },
    "成都": {
        "晴天": [
            {"name": "大熊猫繁育研究基地", "desc": "近距离观赏可爱的大熊猫，了解熊猫保护知识", "indoor": False},
            {"name": "都江堰", "desc": "世界文化遗产，古代水利工程的杰作", "indoor": False},
        ],
        "多云": [
            {"name": "宽窄巷子", "desc": "体验老成都的慢生活，品尝地道川菜小吃", "indoor": False},
            {"name": "锦里古街", "desc": "三国文化圣地，感受成都的民俗风情", "indoor": False},
        ],
        "雨天": [
            {"name": "四川博物院", "desc": "西南地区最大的综合性博物馆，巴蜀文化精华荟萃", "indoor": True},
            {"name": "杜甫草堂", "desc": "唐代大诗人杜甫的故居，感受诗圣的文化气息", "indoor": True},
        ]
    }
}


def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，搜索并推荐旅游景点。

    Args:
        city: 城市名称，例如 "北京"、"上海"
        weather: 天气状况，例如 "晴天"、"雨天"、"多云"

    Returns:
        景点推荐信息

    Examples:
        >>> get_attraction("北京", "晴天")
        '推荐以下景点: 1. 颐和园 - 美丽的皇家园林...'
    """
    # 标准化天气分类
    weather_type = _classify_weather(weather)
    city_normalized = city.strip()

    # 查找景点
    if city_normalized not in ATTRACTIONS_DB:
        return f"抱歉，暂时没有{city_normalized}的景点推荐数据。"

    if weather_type not in ATTRACTIONS_DB[city_normalized]:
        return f"抱歉，暂时没有{weather_type}天气下{city_normalized}的景点推荐。"

    attractions = ATTRACTIONS_DB[city_normalized][weather_type]

    # 构建推荐结果
    result = [f"根据{weather}的天气，为您推荐以下{city}的景点:\n"]
    for i, attraction in enumerate(attractions, 1):
        indoor_flag = "【室内】" if attraction["indoor"] else ""
        result.append(
            f"{i}. {indoor_flag}{attraction['name']}: {attraction['desc']}"
        )

    return "\n".join(result)


def _classify_weather(weather: str) -> str:
    """
    将天气描述分类为标准类型

    Args:
        weather: 天气描述

    Returns:
        标准化后的天气类型
    """
    weather_lower = weather.lower()

    # 雨天判断
    if any(keyword in weather_lower for keyword in ["雨", "rain", "shower"]):
        return "雨天"
    # 晴天判断
    elif any(keyword in weather_lower for keyword in ["晴", "sunny", "clear"]):
        return "晴天"
    # 多云判断（默认）
    else:
        return "多云"


def search_attraction_by_keyword(keyword: str) -> str:
    """
    根据关键词搜索景点

    Args:
        keyword: 搜索关键词，可以是景点名称或描述

    Returns:
        搜索结果
    """
    results = []
    keyword_lower = keyword.lower()

    for city, weather_types in ATTRACTIONS_DB.items():
        for weather_type, attractions in weather_types.items():
            for attraction in attractions:
                if (keyword_lower in attraction["name"].lower() or
                    keyword_lower in attraction["desc"].lower()):
                    results.append({
                        "city": city,
                        "weather": weather_type,
                        "name": attraction["name"],
                        "desc": attraction["desc"]
                    })

    if not results:
        return f"未找到与'{keyword}'相关的景点。"

    output = [f"找到{len(results)}个与'{keyword}'相关的景点:\n"]
    for i, r in enumerate(results, 1):
        output.append(
            f"{i}. [{r['city']}] {r['name']} ({r['weather']}推荐): {r['desc']}"
        )

    return "\n".join(output)


# 工具定义（用于注册到 Agent）
ATTRACTION_TOOL_DEFINITIONS = {
    "get_attraction": {
        "name": "get_attraction",
        "description": "根据城市和天气条件，智能推荐合适的旅游景点。会根据天气状况（晴天/雨天/多云）推荐室内或室外景点。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如'北京'、'上海'、'杭州'、'成都'"
                },
                "weather": {
                    "type": "string",
                    "description": "天气状况，例如'晴天'、'雨天'、'多云'，或者具体的天气描述"
                }
            },
            "required": ["city", "weather"]
        }
    },
    "search_attraction_by_keyword": {
        "name": "search_attraction_by_keyword",
        "description": "根据关键词搜索景点，可以是景点名称或描述",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，例如'博物馆'、'园林'、'历史'"
                }
            },
            "required": ["keyword"]
        }
    }
}
