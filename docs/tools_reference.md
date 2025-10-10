# 工具参考文档

本文档详细介绍 shuyixiao-agent 项目中所有内置工具的使用方法。

## 📚 工具概览

项目内置了 **13 个实用工具**，涵盖时间日期、数学计算、字符串处理、编码解码等多个方面。

### 工具分类

- **时间日期类**：`get_current_time`、`get_date_info`、`calculate_age`
- **数学计算类**：`calculate`、`get_random_number`、`check_prime`
- **字符串处理类**：`string_reverse`、`count_words`
- **编码解码类**：`encode_base64`、`decode_base64`
- **转换工具类**：`convert_temperature`
- **工具生成类**：`generate_uuid`
- **信息检索类**：`search_wikipedia`

---

## 🕐 时间日期类工具

### 1. get_current_time

获取当前的日期和时间。

**函数签名：**
```python
def get_current_time() -> str
```

**参数：**
- 无参数

**返回值：**
- 返回格式化的当前时间字符串（格式：YYYY-MM-DD HH:MM:SS）

**使用示例：**
```python
from src.shuyixiao_agent.tools import get_current_time

current_time = get_current_time()
print(current_time)  # 输出：2025-10-10 15:30:45
```

**Agent 使用示例：**
```
问：现在几点了？
答：当前时间是 2025-10-10 15:30:45
```

---

### 2. get_date_info

获取日期的详细信息，包括星期几、第几天、第几周等。

**函数签名：**
```python
def get_date_info(date_str: Optional[str] = None) -> dict
```

**参数：**
- `date_str` (可选): 日期字符串，格式为 YYYY-MM-DD。不传则使用当前日期。

**返回值：**
```python
{
    "date": "2025-10-10",           # 日期
    "weekday": "周五",               # 星期几
    "day_of_year": 283,             # 一年中的第几天
    "week_of_year": 41,             # 一年中的第几周
    "is_weekend": False             # 是否为周末
}
```

**使用示例：**
```python
from src.shuyixiao_agent.tools import get_date_info

# 查询指定日期
info = get_date_info("2025-12-25")
print(info)

# 查询今天
info = get_date_info()
print(info)
```

**Agent 使用示例：**
```
问：2025-12-25是星期几？
答：2025-12-25是周四，是一年中的第359天，第52周，不是周末。
```

---

### 3. calculate_age

根据出生日期计算年龄。

**函数签名：**
```python
def calculate_age(birth_date: str) -> dict
```

**参数：**
- `birth_date`: 出生日期，格式为 YYYY-MM-DD

**返回值：**
```python
{
    "age_years": 30,                # 年龄（岁）
    "total_days": 10957,            # 总天数
    "birth_date": "1995-01-01",     # 出生日期
    "current_date": "2025-10-10"    # 当前日期
}
```

**使用示例：**
```python
from src.shuyixiao_agent.tools import calculate_age

age_info = calculate_age("1995-06-15")
print(f"年龄：{age_info['age_years']}岁")
print(f"已生活：{age_info['total_days']}天")
```

**Agent 使用示例：**
```
问：1990-01-01出生的人现在多大了？
答：出生于1990-01-01的人现在35岁，已经生活了13066天。
```

---

## 🧮 数学计算类工具

### 4. calculate

计算数学表达式，支持基本的四则运算和括号。

**函数签名：**
```python
def calculate(expression: str) -> float
```

**参数：**
- `expression`: 数学表达式字符串，例如 "2 + 3 * 4"

**返回值：**
- 计算结果（浮点数）

**支持的运算：**
- 加法：`+`
- 减法：`-`
- 乘法：`*`
- 除法：`/`
- 括号：`()`

**使用示例：**
```python
from src.shuyixiao_agent.tools import calculate

result = calculate("(15 + 25) * 3")
print(result)  # 输出：120.0

result = calculate("100 / 4 + 5")
print(result)  # 输出：30.0
```

**Agent 使用示例：**
```
问：帮我计算 123 * 456
答：123 * 456 = 56088
```

**安全性：**
此工具仅允许数字和基本运算符，不支持函数调用，保证安全性。

---

### 5. get_random_number

生成指定范围内的随机整数。

**函数签名：**
```python
def get_random_number(min_value: int = 1, max_value: int = 100) -> int
```

**参数：**
- `min_value` (可选): 最小值（包含），默认为 1
- `max_value` (可选): 最大值（包含），默认为 100

**返回值：**
- 随机整数

**使用示例：**
```python
from src.shuyixiao_agent.tools import get_random_number

# 生成1到100之间的随机数
num = get_random_number()
print(num)

# 生成1到1000之间的随机数
num = get_random_number(1, 1000)
print(num)

# 生成骰子点数
dice = get_random_number(1, 6)
print(f"掷骰子结果：{dice}")
```

**Agent 使用示例：**
```
问：生成一个1到1000之间的随机数
答：生成的随机数是 742
```

---

### 6. check_prime

检查一个数是否为质数。

**函数签名：**
```python
def check_prime(number: int) -> dict
```

**参数：**
- `number`: 要检查的整数

**返回值：**
```python
{
    "number": 17,                   # 被检查的数字
    "is_prime": True,               # 是否为质数
    "reason": "没有找到除1和自身外的因数"  # 原因说明
}
```

**使用示例：**
```python
from src.shuyixiao_agent.tools import check_prime

result = check_prime(17)
print(result)
# {'number': 17, 'is_prime': True, 'reason': '没有找到除1和自身外的因数'}

result = check_prime(18)
print(result)
# {'number': 18, 'is_prime': False, 'reason': '能被2整除'}
```

**Agent 使用示例：**
```
问：97是质数吗？
答：97是质数，没有找到除1和自身外的因数。
```

---

## 🔤 字符串处理类工具

### 7. string_reverse

反转字符串。

**函数签名：**
```python
def string_reverse(text: str) -> str
```

**参数：**
- `text`: 要反转的字符串

**返回值：**
- 反转后的字符串

**使用示例：**
```python
from src.shuyixiao_agent.tools import string_reverse

result = string_reverse("Hello World")
print(result)  # 输出：dlroW olleH

result = string_reverse("Python")
print(result)  # 输出：nohtyP
```

**Agent 使用示例：**
```
问：反转字符串 "hello world"
答：反转后的字符串是 "dlrow olleh"
```

---

### 8. count_words

统计文本的字符数、单词数和行数。

**函数签名：**
```python
def count_words(text: str) -> dict
```

**参数：**
- `text`: 要统计的文本

**返回值：**
```python
{
    "total_characters": 50,              # 总字符数（包含空格）
    "total_characters_no_spaces": 42,    # 总字符数（不含空格）
    "total_words": 8,                    # 单词数
    "total_lines": 3                     # 行数
}
```

**使用示例：**
```python
from src.shuyixiao_agent.tools import count_words

text = "Hello World! This is a test."
stats = count_words(text)
print(stats)
# {
#   'total_characters': 28,
#   'total_characters_no_spaces': 23,
#   'total_words': 6,
#   'total_lines': 1
# }
```

**Agent 使用示例：**
```
问：统计这段文本的字数：Hello World! This is a test.
答：该文本共有28个字符（包含空格），23个字符（不含空格），6个单词，1行。
```

---

## 🔐 编码解码类工具

### 9. encode_base64

将文本进行 Base64 编码。

**函数签名：**
```python
def encode_base64(text: str) -> str
```

**参数：**
- `text`: 要编码的文本

**返回值：**
- Base64 编码后的字符串

**使用示例：**
```python
from src.shuyixiao_agent.tools import encode_base64

encoded = encode_base64("Hello World")
print(encoded)  # 输出：SGVsbG8gV29ybGQ=
```

**Agent 使用示例：**
```
问：对"Hello World"进行base64编码
答：编码后的结果是 SGVsbG8gV29ybGQ=
```

---

### 10. decode_base64

将 Base64 编码的字符串解码为文本。

**函数签名：**
```python
def decode_base64(encoded_text: str) -> str
```

**参数：**
- `encoded_text`: Base64 编码的字符串

**返回值：**
- 解码后的文本

**使用示例：**
```python
from src.shuyixiao_agent.tools import decode_base64

decoded = decode_base64("SGVsbG8gV29ybGQ=")
print(decoded)  # 输出：Hello World
```

**Agent 使用示例：**
```
问：解码这个base64字符串：SGVsbG8gV29ybGQ=
答：解码后的文本是 "Hello World"
```

**错误处理：**
如果输入不是有效的 Base64 字符串，会抛出 ValueError。

---

## 🔄 转换工具类

### 11. convert_temperature

温度单位转换，支持摄氏度(C)、华氏度(F)、开尔文(K)之间的转换。

**函数签名：**
```python
def convert_temperature(value: float, from_unit: str, to_unit: str) -> float
```

**参数：**
- `value`: 温度值
- `from_unit`: 源温度单位（C/F/K）
- `to_unit`: 目标温度单位（C/F/K）

**返回值：**
- 转换后的温度值（保留2位小数）

**支持的单位：**
- `C`: 摄氏度（Celsius）
- `F`: 华氏度（Fahrenheit）
- `K`: 开尔文（Kelvin）

**使用示例：**
```python
from src.shuyixiao_agent.tools import convert_temperature

# 摄氏度转华氏度
temp = convert_temperature(25, "C", "F")
print(temp)  # 输出：77.0

# 华氏度转摄氏度
temp = convert_temperature(77, "F", "C")
print(temp)  # 输出：25.0

# 摄氏度转开尔文
temp = convert_temperature(0, "C", "K")
print(temp)  # 输出：273.15
```

**Agent 使用示例：**
```
问：25摄氏度等于多少华氏度？
答：25°C = 77°F

问：100华氏度是多少摄氏度？
答：100°F = 37.78°C
```

**转换公式：**
- 摄氏度 → 华氏度：F = C × 9/5 + 32
- 华氏度 → 摄氏度：C = (F - 32) × 5/9
- 摄氏度 → 开尔文：K = C + 273.15
- 开尔文 → 摄氏度：C = K - 273.15

---

## 🔧 工具生成类

### 12. generate_uuid

生成 UUID（通用唯一识别码）。

**函数签名：**
```python
def generate_uuid(version: int = 4) -> str
```

**参数：**
- `version` (可选): UUID 版本，支持 1 或 4，默认为 4

**返回值：**
- UUID 字符串

**UUID 版本说明：**
- **版本 1**：基于时间戳和 MAC 地址生成
- **版本 4**：基于随机数生成（推荐）

**使用示例：**
```python
from src.shuyixiao_agent.tools import generate_uuid

# 生成UUID v4（推荐）
uuid = generate_uuid()
print(uuid)  # 输出：550e8400-e29b-41d4-a716-446655440000

# 生成UUID v1
uuid = generate_uuid(version=1)
print(uuid)  # 输出：a8098c1a-f86e-11da-bd1a-00112444be1e
```

**Agent 使用示例：**
```
问：生成一个UUID
答：生成的UUID是 550e8400-e29b-41d4-a716-446655440000
```

**应用场景：**
- 生成唯一的订单号
- 创建唯一的会话ID
- 数据库记录的唯一标识符
- 文件命名

---

## 📖 信息检索类

### 13. search_wikipedia

搜索维基百科获取信息（当前为模拟实现）。

**函数签名：**
```python
def search_wikipedia(query: str) -> str
```

**参数：**
- `query`: 搜索关键词

**返回值：**
- 搜索结果摘要（字符串）

**使用示例：**
```python
from src.shuyixiao_agent.tools import search_wikipedia

result = search_wikipedia("Python编程语言")
print(result)
```

**Agent 使用示例：**
```
问：搜索维基百科上关于Python的信息
答：关于 'Python' 的维基百科搜索结果：...
```

**注意：**
这是一个模拟实现。在实际应用中，可以替换为真实的维基百科 API 调用。

---

## 🚀 批量使用工具

### 方法1：手动注册

```python
from src.shuyixiao_agent.agents.tool_agent import ToolAgent
from src.shuyixiao_agent.tools import (
    get_current_time, 
    calculate, 
    get_random_number
)

agent = ToolAgent()

# 逐个注册工具
agent.register_tool(
    name="get_current_time",
    func=get_current_time,
    description="获取当前时间",
    parameters={"type": "object", "properties": {}, "required": []}
)

agent.register_tool(
    name="calculate",
    func=calculate,
    description="计算数学表达式",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "数学表达式"}
        },
        "required": ["expression"]
    }
)
```

### 方法2：批量注册（推荐）

```python
from src.shuyixiao_agent.agents.tool_agent import ToolAgent
from src.shuyixiao_agent.tools import get_basic_tools

agent = ToolAgent()

# 批量注册所有基础工具
for tool in get_basic_tools():
    agent.register_tool(
        name=tool["name"],
        func=tool["func"],
        description=tool["description"],
        parameters=tool["parameters"]
    )

# 现在可以使用所有13个工具
response = agent.run("现在几点？帮我计算25*4，然后生成一个随机数")
print(response)
```

---

## 💡 最佳实践

### 1. 工具选择
- 根据任务需求选择合适的工具
- 不需要所有工具时，可以只注册必要的工具
- 工具越少，模型决策越快

### 2. 错误处理
- 所有工具都会对输入进行验证
- 捕获可能的异常并提供友好的错误信息
- 建议在生产环境中添加日志记录

### 3. 性能优化
- 批量注册工具时使用 `get_basic_tools()`
- 避免在循环中重复创建 Agent
- 合理设置 `max_iterations` 避免无限循环

### 4. 扩展工具
如果内置工具不够用，可以自定义工具：

```python
def custom_tool(param1: str, param2: int) -> str:
    """自定义工具函数"""
    # 实现你的逻辑
    return f"处理结果：{param1} - {param2}"

# 注册自定义工具
agent.register_tool(
    name="custom_tool",
    func=custom_tool,
    description="你的工具描述",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数1说明"},
            "param2": {"type": "integer", "description": "参数2说明"}
        },
        "required": ["param1", "param2"]
    }
)
```

---

## 📚 相关文档

- [快速开始](getting_started.md)
- [API 参考](api_reference.md)
- [示例代码](../examples/README.md)
- [LangGraph 架构](langgraph_architecture.md)

---

## 🤝 贡献

欢迎贡献新的工具！如果你有好的工具想法，请：

1. Fork 本仓库
2. 在 `src/shuyixiao_agent/tools/basic_tools.py` 中添加新工具
3. 更新 `TOOL_DEFINITIONS` 和 `get_basic_tools()`
4. 添加测试用例
5. 更新本文档
6. 提交 Pull Request

---

**如有疑问，请在 [GitHub Issues](https://github.com/your-username/shuyixiao-agent/issues) 中提出。**

