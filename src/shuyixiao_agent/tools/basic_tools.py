"""
基础工具集

提供一些基础的工具供 Agent 使用
"""

from datetime import datetime
import operator
import random
import uuid
import base64
from typing import Optional


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


def get_random_number(min_value: int = 1, max_value: int = 100) -> int:
    """
    生成指定范围内的随机整数
    
    Args:
        min_value: 最小值（包含）
        max_value: 最大值（包含）
        
    Returns:
        随机整数
    """
    return random.randint(min_value, max_value)


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    温度单位转换
    
    Args:
        value: 温度值
        from_unit: 源单位（C/F/K）
        to_unit: 目标单位（C/F/K）
        
    Returns:
        转换后的温度值
    """
    # 先转换为摄氏度
    if from_unit.upper() == 'C':
        celsius = value
    elif from_unit.upper() == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit.upper() == 'K':
        celsius = value - 273.15
    else:
        raise ValueError(f"不支持的温度单位: {from_unit}")
    
    # 再从摄氏度转换为目标单位
    if to_unit.upper() == 'C':
        return round(celsius, 2)
    elif to_unit.upper() == 'F':
        return round(celsius * 9/5 + 32, 2)
    elif to_unit.upper() == 'K':
        return round(celsius + 273.15, 2)
    else:
        raise ValueError(f"不支持的温度单位: {to_unit}")


def string_reverse(text: str) -> str:
    """
    反转字符串
    
    Args:
        text: 要反转的字符串
        
    Returns:
        反转后的字符串
    """
    return text[::-1]


def count_words(text: str) -> dict:
    """
    统计字符串中的单词和字符数量
    
    Args:
        text: 要统计的文本
        
    Returns:
        包含统计信息的字典
    """
    words = text.split()
    return {
        "total_characters": len(text),
        "total_characters_no_spaces": len(text.replace(" ", "")),
        "total_words": len(words),
        "total_lines": len(text.split('\n'))
    }


def get_date_info(date_str: Optional[str] = None) -> dict:
    """
    获取日期信息
    
    Args:
        date_str: 日期字符串（格式：YYYY-MM-DD），不传则使用当前日期
        
    Returns:
        包含日期信息的字典
    """
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式错误，应为 YYYY-MM-DD")
    else:
        date = datetime.now()
    
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "weekday": weekday_names[date.weekday()],
        "day_of_year": date.timetuple().tm_yday,
        "week_of_year": date.isocalendar()[1],
        "is_weekend": date.weekday() >= 5
    }


def calculate_age(birth_date: str) -> dict:
    """
    根据出生日期计算年龄
    
    Args:
        birth_date: 出生日期（格式：YYYY-MM-DD）
        
    Returns:
        包含年龄信息的字典
    """
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期格式错误，应为 YYYY-MM-DD")
    
    today = datetime.now()
    
    # 计算年龄
    age_years = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age_years -= 1
    
    # 计算总天数
    total_days = (today - birth).days
    
    return {
        "age_years": age_years,
        "total_days": total_days,
        "birth_date": birth_date,
        "current_date": today.strftime("%Y-%m-%d")
    }


def generate_uuid(version: int = 4) -> str:
    """
    生成UUID
    
    Args:
        version: UUID版本（1或4）
        
    Returns:
        UUID字符串
    """
    if version == 1:
        return str(uuid.uuid1())
    elif version == 4:
        return str(uuid.uuid4())
    else:
        raise ValueError("只支持UUID版本1和4")


def encode_base64(text: str) -> str:
    """
    Base64编码
    
    Args:
        text: 要编码的文本
        
    Returns:
        Base64编码后的字符串
    """
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


def decode_base64(encoded_text: str) -> str:
    """
    Base64解码
    
    Args:
        encoded_text: Base64编码的字符串
        
    Returns:
        解码后的文本
    """
    try:
        decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Base64解码失败: {str(e)}")


def check_prime(number: int) -> dict:
    """
    检查一个数是否为质数
    
    Args:
        number: 要检查的数字
        
    Returns:
        包含检查结果的字典
    """
    if number < 2:
        return {
            "number": number,
            "is_prime": False,
            "reason": "质数必须大于1"
        }
    
    if number == 2:
        return {
            "number": number,
            "is_prime": True,
            "reason": "2是最小的质数"
        }
    
    if number % 2 == 0:
        return {
            "number": number,
            "is_prime": False,
            "reason": "偶数（除2外）不是质数"
        }
    
    # 检查奇数因子
    for i in range(3, int(number ** 0.5) + 1, 2):
        if number % i == 0:
            return {
                "number": number,
                "is_prime": False,
                "reason": f"能被{i}整除"
            }
    
    return {
        "number": number,
        "is_prime": True,
        "reason": "没有找到除1和自身外的因数"
    }


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
    },
    "get_random_number": {
        "name": "get_random_number",
        "description": "生成指定范围内的随机整数",
        "parameters": {
            "type": "object",
            "properties": {
                "min_value": {
                    "type": "integer",
                    "description": "最小值（包含），默认为1"
                },
                "max_value": {
                    "type": "integer",
                    "description": "最大值（包含），默认为100"
                }
            },
            "required": []
        }
    },
    "convert_temperature": {
        "name": "convert_temperature",
        "description": "温度单位转换，支持摄氏度(C)、华氏度(F)、开尔文(K)之间的转换",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "要转换的温度值"
                },
                "from_unit": {
                    "type": "string",
                    "description": "源温度单位：C（摄氏度）、F（华氏度）、K（开尔文）"
                },
                "to_unit": {
                    "type": "string",
                    "description": "目标温度单位：C（摄氏度）、F（华氏度）、K（开尔文）"
                }
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    },
    "string_reverse": {
        "name": "string_reverse",
        "description": "反转字符串",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要反转的字符串"
                }
            },
            "required": ["text"]
        }
    },
    "count_words": {
        "name": "count_words",
        "description": "统计文本的字符数、单词数和行数",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要统计的文本"
                }
            },
            "required": ["text"]
        }
    },
    "get_date_info": {
        "name": "get_date_info",
        "description": "获取日期的详细信息，包括星期几、第几天、第几周等",
        "parameters": {
            "type": "object",
            "properties": {
                "date_str": {
                    "type": "string",
                    "description": "日期字符串（格式：YYYY-MM-DD），不传则使用当前日期"
                }
            },
            "required": []
        }
    },
    "calculate_age": {
        "name": "calculate_age",
        "description": "根据出生日期计算年龄",
        "parameters": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期（格式：YYYY-MM-DD）"
                }
            },
            "required": ["birth_date"]
        }
    },
    "generate_uuid": {
        "name": "generate_uuid",
        "description": "生成UUID（通用唯一识别码）",
        "parameters": {
            "type": "object",
            "properties": {
                "version": {
                    "type": "integer",
                    "description": "UUID版本，支持1或4，默认为4"
                }
            },
            "required": []
        }
    },
    "encode_base64": {
        "name": "encode_base64",
        "description": "将文本进行Base64编码",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要编码的文本"
                }
            },
            "required": ["text"]
        }
    },
    "decode_base64": {
        "name": "decode_base64",
        "description": "将Base64编码的字符串解码为文本",
        "parameters": {
            "type": "object",
            "properties": {
                "encoded_text": {
                    "type": "string",
                    "description": "Base64编码的字符串"
                }
            },
            "required": ["encoded_text"]
        }
    },
    "check_prime": {
        "name": "check_prime",
        "description": "检查一个数是否为质数",
        "parameters": {
            "type": "object",
            "properties": {
                "number": {
                    "type": "integer",
                    "description": "要检查的整数"
                }
            },
            "required": ["number"]
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
        },
        {
            "name": "get_random_number",
            "func": get_random_number,
            "description": "生成指定范围内的随机整数",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_value": {
                        "type": "integer",
                        "description": "最小值（包含），默认为1"
                    },
                    "max_value": {
                        "type": "integer",
                        "description": "最大值（包含），默认为100"
                    }
                },
                "required": []
            }
        },
        {
            "name": "convert_temperature",
            "func": convert_temperature,
            "description": "温度单位转换，支持摄氏度(C)、华氏度(F)、开尔文(K)之间的转换",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "要转换的温度值"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "源温度单位：C（摄氏度）、F（华氏度）、K（开尔文）"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "目标温度单位：C（摄氏度）、F（华氏度）、K（开尔文）"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        },
        {
            "name": "string_reverse",
            "func": string_reverse,
            "description": "反转字符串",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要反转的字符串"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "count_words",
            "func": count_words,
            "description": "统计文本的字符数、单词数和行数",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要统计的文本"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "get_date_info",
            "func": get_date_info,
            "description": "获取日期的详细信息，包括星期几、第几天、第几周等",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {
                        "type": "string",
                        "description": "日期字符串（格式：YYYY-MM-DD），不传则使用当前日期"
                    }
                },
                "required": []
            }
        },
        {
            "name": "calculate_age",
            "func": calculate_age,
            "description": "根据出生日期计算年龄",
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_date": {
                        "type": "string",
                        "description": "出生日期（格式：YYYY-MM-DD）"
                    }
                },
                "required": ["birth_date"]
            }
        },
        {
            "name": "generate_uuid",
            "func": generate_uuid,
            "description": "生成UUID（通用唯一识别码）",
            "parameters": {
                "type": "object",
                "properties": {
                    "version": {
                        "type": "integer",
                        "description": "UUID版本，支持1或4，默认为4"
                    }
                },
                "required": []
            }
        },
        {
            "name": "encode_base64",
            "func": encode_base64,
            "description": "将文本进行Base64编码",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要编码的文本"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "decode_base64",
            "func": decode_base64,
            "description": "将Base64编码的字符串解码为文本",
            "parameters": {
                "type": "object",
                "properties": {
                    "encoded_text": {
                        "type": "string",
                        "description": "Base64编码的字符串"
                    }
                },
                "required": ["encoded_text"]
            }
        },
        {
            "name": "check_prime",
            "func": check_prime,
            "description": "检查一个数是否为质数",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "integer",
                        "description": "要检查的整数"
                    }
                },
                "required": ["number"]
            }
        }
    ]
