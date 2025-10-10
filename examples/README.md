# 示例代码

本目录包含了各种使用示例，帮助你快速上手 shuyixiao-agent 项目。

## 示例列表

### 01_simple_chat.py - 简单对话
最基础的示例，演示如何创建一个简单的对话 Agent。

**运行方式：**
```bash
python examples/01_simple_chat.py
```

**学习要点：**
- 如何初始化 SimpleAgent
- 如何进行单轮对话
- 如何实现交互式对话循环

---

### 02_tool_agent.py - 带工具的 Agent
演示如何创建一个可以调用工具的 Agent。

**运行方式：**
```bash
python examples/02_tool_agent.py
```

**学习要点：**
- 如何初始化 ToolAgent
- 如何注册工具
- Agent 如何自动决定何时调用工具
- 工具调用的完整流程

---

### 03_custom_tool.py - 自定义工具
演示如何创建和注册自己的自定义工具。

**运行方式：**
```bash
python examples/03_custom_tool.py
```

**学习要点：**
- 如何定义工具函数
- 如何编写工具描述和参数定义
- 如何处理工具的输入输出
- 实用的自定义工具示例

---

### 04_api_client.py - API 客户端
演示如何直接使用码云 AI API 客户端。

**运行方式：**
```bash
python examples/04_api_client.py
```

**学习要点：**
- GiteeAIClient 的基本使用
- 多轮对话的实现
- 如何调整模型参数（temperature、max_tokens 等）
- 如何查看 API 响应详情

---

### 05_all_tools_demo.py - 完整工具集演示
演示所有13个内置工具的使用方法。

**运行方式：**
```bash
python examples/05_all_tools_demo.py
```

**学习要点：**
- 如何批量注册多个工具
- 时间和日期工具的使用（当前时间、日期信息、年龄计算）
- 数学工具的使用（计算器、随机数、质数检查）
- 字符串工具的使用（反转、统计）
- 编码工具的使用（Base64编码/解码）
- 转换工具的使用（温度转换）
- UUID生成工具的使用

**包含的工具：**
1. `get_current_time` - 获取当前时间
2. `calculate` - 数学计算
3. `search_wikipedia` - 维基百科搜索
4. `get_random_number` - 生成随机数
5. `convert_temperature` - 温度转换
6. `string_reverse` - 字符串反转
7. `count_words` - 文本统计
8. `get_date_info` - 日期信息
9. `calculate_age` - 年龄计算
10. `generate_uuid` - UUID生成
11. `encode_base64` - Base64编码
12. `decode_base64` - Base64解码
13. `check_prime` - 质数检查

---

### 06_ai_powered_tools_demo.py - AI驱动工具演示 🚀 **推荐**

**这是最重要的示例！** 演示真正需要大模型参与的智能工具，而不是简单的硬编码逻辑。

**运行方式：**
```bash
python examples/06_ai_powered_tools_demo.py
```

**学习要点：**
- 什么是真正的AI工具
- AI工具与普通工具的区别
- 如何使用AI进行代码审查
- 如何使用AI生成创意
- 如何使用AI优化内容
- 如何使用AI辅助决策

**包含的AI工具：**
1. `web_content_analyzer` - 智能网页内容分析（理解、提取、摘要）
2. `text_quality_analyzer` - 文本质量分析（评估、发现问题、改进建议）
3. `creative_idea_generator` - 创意生成（发散思维、创新、可行性）
4. `code_review_assistant` - 代码审查（理解逻辑、发现问题、优化）
5. `decision_analyzer` - 决策分析（多维度分析、权衡、建议）
6. `data_insight_generator` - 数据洞察（理解数据、发现规律）
7. `content_improver` - 内容优化（理解意图、改进表达）
8. `problem_solver` - 问题解决（分解问题、系统性方案）
9. `meeting_summarizer` - 会议总结（提取要点、结构化）
10. `learning_path_designer` - 学习路径设计（知识体系、规划）

**为什么这些工具重要？**
- ✅ 需要深度理解和分析能力
- ✅ 需要创造性和推理能力
- ✅ 需要专业知识和经验
- ✅ 传统编程难以实现
- ✅ 真正体现AI的价值

**对比旧工具：**
- ❌ 旧工具：获取时间、计算、字符串反转 - Java也能做
- ✅ 新工具：代码审查、创意生成、决策分析 - 需要AI智能

📖 **详细了解：** [AI工具设计哲学](../docs/ai_tools_philosophy.md)

---

## 准备工作

在运行示例之前，请确保：

1. **已安装依赖：**
   ```bash
   poetry install
   ```

2. **已配置环境变量：**
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 中填入你的码云 AI API Key

3. **已购买资源包：**
   - 访问 [码云 AI 模型广场](https://ai.gitee.com/serverless)
   - 购买相应的模型资源包

## 运行示例

### 使用 Poetry（推荐）

```bash
# 激活虚拟环境
poetry shell

# 运行示例
python examples/01_simple_chat.py
```

### 直接运行

```bash
python examples/01_simple_chat.py
```

## 常见问题

### 1. 提示 "未提供 API Key"
- 确保已创建 `.env` 文件
- 确保 `.env` 中有 `GITEE_AI_API_KEY=你的密钥`

### 2. API 请求失败
- 检查 API Key 是否有效
- 检查是否购买了对应模型的资源包
- 检查网络连接是否正常

### 3. 模块导入错误
- 确保已安装所有依赖：`poetry install`
- 确保在项目根目录运行示例

## 下一步

- 阅读 [完整文档](../docs/)
- 查看 [API 参考](../docs/api_reference.md)
- 尝试修改示例代码，实现自己的功能

