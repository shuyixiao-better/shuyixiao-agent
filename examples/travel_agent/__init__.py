"""
智能旅行助手 Agent 示例

基于 Datawhale《Hello-Agents》教程 1.3 节实现
演示 Thought-Action-Observation 循环模式
"""

from examples.travel_agent.weather_tools import (
    get_weather,
    get_weather_forecast,
    WEATHER_TOOL_DEFINITIONS
)

from examples.travel_agent.attraction_tools import (
    get_attraction,
    search_attraction_by_keyword,
    ATTRACTION_TOOL_DEFINITIONS
)

__all__ = [
    "get_weather",
    "get_weather_forecast",
    "WEATHER_TOOL_DEFINITIONS",
    "get_attraction",
    "search_attraction_by_keyword",
    "ATTRACTION_TOOL_DEFINITIONS",
]
