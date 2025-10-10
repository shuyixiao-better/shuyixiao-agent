"""
基础工具集

提供一些基础的工具供 Agent 使用
"""

from datetime import datetime
import operator


def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        当前时间的字符串表示
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> float:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式字符串，例如 "2 + 3 * 4"
        
    Returns:
        计算结果
    """
    # 安全的数学表达式求值
    # 只允许数字和基本运算符
    allowed_chars = set("0123456789+-*/(). ")
    
    if not all(c in allowed_chars for c in expression):
        raise ValueError("表达式包含不允许的字符")
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"计算错误: {str(e)}")


def search_wikipedia(query: str) -> str:
    """
    搜索维基百科（模拟实现）
    
    Args:
        query: 搜索关键词
        
    Returns:
        搜索结果摘要
    """
    # 这是一个模拟实现
    # 实际使用时可以调用真实的维基百科 API
    return f"关于 '{query}' 的维基百科搜索结果：这是一个示例工具的模拟返回。在实际应用中，这里会调用真实的维基百科 API。"


# 工具定义（用于注册到 Agent）
TOOL_DEFINITIONS = {
    "get_current_time": {
        "name": "get_current_time",
        "description": "获取当前的日期和时间",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "calculate": {
        "name": "calculate",
        "description": "计算数学表达式。支持加减乘除和括号。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，例如 '2 + 3 * 4'"
                }
            },
            "required": ["expression"]
        }
    },
    "search_wikipedia": {
        "name": "search_wikipedia",
        "description": "搜索维基百科获取信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                }
            },
            "required": ["query"]
        }
    }
}


def get_basic_tools():
    """
    获取基础工具列表，用于注册到 Agent
    
    Returns:
        工具信息列表
    """
    return [
        {
            "name": "get_current_time",
            "func": get_current_time,
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "calculate",
            "func": calculate,
            "description": "计算数学表达式。支持加减乘除和括号。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如 '2 + 3 * 4'"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "search_wikipedia",
            "func": search_wikipedia,
            "description": "搜索维基百科获取信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["query"]
            }
        }
    ]
