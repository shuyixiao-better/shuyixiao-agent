"""
旅行助手 - 天气查询工具

提供天气查询功能，支持真实 API 调用
"""

import requests
from typing import Optional


def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。

    Args:
        city: 城市名称，例如 "北京"、"上海"

    Returns:
        天气信息的自然语言描述

    Examples:
        >>> get_weather("北京")
        '北京当前天气:晴天，气温26摄氏度'
    """
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # 发起网络请求
        response = requests.get(url, timeout=10)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status()
        # 解析返回的JSON数据
        data = response.json()

        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        humidity = current_condition['humidity']
        wind_speed = current_condition['windspeedKmph']

        # 格式化成自然语言返回
        return (
            f"{city}当前天气: {weather_desc}，"
            f"气温{temp_c}摄氏度，"
            f"湿度{humidity}%，"
            f"风速{wind_speed}公里/小时"
        )

    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误: 查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误: 解析天气数据失败，可能是城市名称无效 - {e}"


def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    获取未来几天的天气预报

    Args:
        city: 城市名称
        days: 预报天数（1-3天），默认3天

    Returns:
        天气预报信息
    """
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 获取天气预报数据
        weather_list = data.get('weather', [])[:days]

        if not weather_list:
            return f"错误: 未获取到{city}的天气预报数据"

        result = [f"{city}未来{len(weather_list)}天天气预报:"]
        for i, day_data in enumerate(weather_list, 1):
            date = day_data['date']
            avg_temp = (int(day_data['maxtempC']) + int(day_data['mintempC'])) // 2
            weather_desc = day_data['hourly'][0]['weatherDesc'][0]['value']
            result.append(f"  {date}: {weather_desc}，平均气温约{avg_temp}摄氏度")

        return "\n".join(result)

    except Exception as e:
        return f"错误: 获取天气预报失败 - {e}"


# 工具定义（用于注册到 Agent）
WEATHER_TOOL_DEFINITIONS = {
    "get_weather": {
        "name": "get_weather",
        "description": "查询指定城市的实时天气信息，包括温度、湿度、风速等",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如'北京'、'上海'、'深圳'"
                }
            },
            "required": ["city"]
        }
    },
    "get_weather_forecast": {
        "name": "get_weather_forecast",
        "description": "获取指定城市未来几天的天气预报",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                },
                "days": {
                    "type": "integer",
                    "description": "预报天数，默认3天，最多3天"
                }
            },
            "required": ["city"]
        }
    }
}
