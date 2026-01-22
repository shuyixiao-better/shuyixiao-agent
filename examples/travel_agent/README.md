# 智能旅行助手 Agent 示例

基于 [Datawhale《Hello-Agents》](https://datawhalechina.github.io/hello-agents/) 教程 1.3 节 "动手体验：5 分钟实现第一个智能体" 实现，演示 **Thought-Action-Observation** 循环模式。

使用 [Moark (模力方舟)](https://moark.com) API 进行模型调用，该 API 兼容 OpenAI SDK。

## 功能说明

这个智能旅行助手能够：
1. 接收用户的自然语言请求（如"查询北京天气并推荐景点"）
2. 自动分析任务并分解为多个步骤
3. 调用天气查询工具获取实时天气
4. 根据天气情况智能推荐合适的景点（晴天推荐室外景点，雨天推荐室内景点）
5. 综合信息给出最终建议

## 项目结构

```
travel_agent/
├── __init__.py              # 模块初始化文件
├── weather_tools.py         # 天气查询工具（使用 wttr.in API）
├── attraction_tools.py      # 景点推荐工具（基于天气智能推荐）
├── travel_agent_demo.py     # 主程序演示
└── README.md               # 本文档
```

## 配置说明

### 1. 环境变量配置

在项目根目录的 `.env` 文件中配置以下内容：

```bash
# Moark API 密钥（必填）
GITEE_AI_API_KEY=your_api_key_here

# Moark API 基础 URL（可选，默认值如下）
GITEE_AI_BASE_URL=https://api.moark.com/v1

# 默认模型名称（可选）
GITEE_AI_MODEL=DeepSeek-V3
```

### 2. 获取 API 密钥

访问 [Moark (模力方舟)](https://moark.com) 注册账号并获取 API 密钥。

## 运行示例

### 方式一：命令行运行

```bash
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent
python -m examples.travel_agent.travel_agent_demo
```

### 方式二：在 PyCharm 中运行

1. 右键点击 `travel_agent_demo.py`
2. 选择 "Run 'travel_agent_demo'"
3. 确保运行配置中已设置 `GITEE_AI_API_KEY` 环境变量

## 示例输出

```
============================================================
智能旅行助手
============================================================

用户输入: 你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。

--- 循环 1 ---

正在调用大语言模型...
模型输出:
Thought: 首先需要获取北京今天的天气情况，之后再根据天气情况来推荐旅游景点。
Action: get_weather(city="北京")

Observation: 北京当前天气: 晴天，气温26摄氏度，湿度45%，风速10公里/小时

============================================================

--- 循环 2 ---

正在调用大语言模型...
模型输出:
Thought: 现在已经知道了北京今天的天气是晴朗且温度适中，接下来可以基于这个信息来推荐一个适合的旅游景点了。
Action: get_attraction(city="北京", weather="晴天")

Observation: 根据晴天的天气，为您推荐以下北京的景点:
1. 颐和园: 美丽的皇家园林，可以泛舟昆明湖，欣赏湖景和古建筑
2. 八达岭长城: 壮观的世界文化遗产，体验'不到长城非好汉'的豪迈
3. 天坛公园: 明清两代皇帝祭祀上天的场所，建筑宏伟，环境优美

============================================================

--- 循环 3 ---

正在调用大语言模型...
模型输出:
Thought: 已经获得了适合晴天游览的景点建议，现在可以根据这些信息给用户提供满意的答复。
Action: Finish[今天北京的天气是晴朗的，气温26摄氏度，非常适合外出游玩。我推荐您去颐和园欣赏美丽的湖景和古建筑，或者前往八达岭长城体验其壮观的景观和深厚的历史意义。天坛公园也是不错的选择，建筑宏伟，环境优美。希望您有一个愉快的旅行！]

任务完成！

最终答案: 今天北京的天气是晴朗的，气温26摄氏度，非常适合外出游玩。我推荐您去颐和园欣赏美丽的湖景和古建筑，或者前往八达岭长城体验其壮观的景观和深厚的历史意义。天坛公园也是不错的选择，建筑宏伟，环境优美。希望您有一个愉快的旅行！
```

## Thought-Action-Observation 循环说明

这是本示例核心的智能体循环模式：

1. **Thought（思考）**: Agent 分析当前情况，规划下一步行动
2. **Action（行动）**: Agent 执行具体的工具调用
3. **Observation（观察）**: Agent 获取工具执行的结果

```
用户请求
    ↓
┌─────────┐
│ Thought │ ← 分析任务，规划下一步
└────┬────┘
     ↓
┌─────────┐
│ Action  │ ← 调用工具
└────┬────┘
     ↓
┌─────────┐
│Observ.  │ ← 获取结果
└────┬────┘
     ↓
   是否完成？
    ↙ ↘
  是    否
  ↓     ↓
返回结果  继续循环
```

## API 调用说明

本示例使用 Moark (模力方舟) 的聊天补全 API，兼容 OpenAI SDK 格式：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.moark.com/v1",
    api_key="your_api_key",
)

response = client.chat.completions.create(
    model="DeepSeek-V3",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
)
```

详细的 API 文档请参考：https://moark.com/docs/openapi/v1

## 工具说明

### 天气查询工具 (get_weather)
- **功能**: 调用 wttr.in API 获取实时天气
- **参数**: city (城市名称)
- **返回**: 天气描述、温度、湿度、风速等信息

### 景点推荐工具 (get_attraction)
- **功能**: 根据城市和天气智能推荐景点
- **参数**: city (城市名称), weather (天气状况)
- **返回**: 根据天气推荐的室内/室外景点列表

## 扩展建议

1. **添加更多城市**: 在 `attraction_tools.py` 的 `ATTRACTIONS_DB` 中添加更多城市的景点数据
2. **接入真实搜索 API**: 替换模拟的景点推荐，接入真实的旅游搜索 API
3. **增加记忆功能**: 让 Agent 记住用户的偏好（如喜欢历史文化、预算范围等）
4. **多轮对话优化**: 改进交互流程，支持用户实时反馈和调整

## 参考资源

- [Datawhale Hello-Agents 教程](https://datawhalechina.github.io/hello-agents/)
- [Moark (模力方舟) API 文档](https://moark.com/docs/openapi/v1)
- [wttr.in 天气 API](https://wttr.in)
