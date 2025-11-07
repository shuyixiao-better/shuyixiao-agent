# Prompt Chaining Agent 使用指南

## 🔗 什么是 Prompt Chaining（提示链）？

Prompt Chaining（提示链）是一种强大的 Agentic Design Pattern，它将复杂任务分解为一系列更小、更易管理的子任务。每个子任务通过专门的提示进行处理，前一步的输出作为下一步的输入，形成链式依赖。

### 核心优势

1. **模块化** - 将复杂任务分解为可管理的步骤
2. **可控性** - 每一步都有明确的输入输出
3. **可调试** - 容易定位问题所在的环节
4. **可复用** - 单个步骤可以在不同链中复用
5. **高质量** - 专注的提示通常产生更好的结果

### 工作原理

```
用户输入 → [步骤1] → 输出1 → [步骤2] → 输出2 → ... → 最终结果
```

每个步骤：
- 接收上一步的输出作为输入
- 使用专门设计的提示词处理
- 生成输出传递给下一步

## 📦 快速开始

### 1. 命令行使用

#### 简单示例（3个快速体验）

```bash
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent
python examples/11_prompt_chaining_simple.py
```

这个脚本提供了3个简单示例：
- **示例1**: 翻译改进链 - 中文→英文→改进→润色
- **示例2**: 博客文章生成链 - 标题→大纲→内容→互动元素
- **示例3**: 问题解决链 - 理解→头脑风暴→评估→计划

#### 完整功能演示（5个实用场景）

```bash
python examples/10_prompt_chaining_demo.py
```

这个脚本提供了5个完整的实用场景：

**场景1：文档生成链** 📄
- 步骤：生成大纲 → 撰写内容 → 添加示例 → 优化润色
- 适用：技术文档、教程、说明书等
- 示例输入：`Python 异步编程入门`

**场景2：代码审查链** 🔍
- 步骤：理解代码 → 检查问题 → 提出建议 → 生成报告
- 适用：代码审查、质量分析
- 示例输入：粘贴你的代码片段

**场景3：研究规划链** 🔬
- 步骤：问题分析 → 文献综述 → 研究方法 → 时间规划
- 适用：学术研究、技术调研
- 示例输入：`如何优化深度学习模型的训练效率？`

**场景4：故事创作链** 📖
- 步骤：构思情节 → 角色塑造 → 撰写初稿 → 润色完善
- 适用：创意写作、剧本创作
- 示例输入：`时间旅行者的困境`

**场景5：产品分析链** 💡
- 步骤：需求理解 → 功能设计 → 技术方案 → 实施计划
- 适用：产品规划、需求分析
- 示例输入：`一个帮助开发者快速搭建API的工具`

### 2. Web 界面使用

启动 Web 服务：

```bash
python run_web.py
```

然后访问 `http://localhost:8001`，你可以：

1. 选择 Prompt Chaining 功能
2. 选择场景类型（文档生成、代码审查等）
3. 输入内容
4. 实时查看每个步骤的执行过程和结果
5. 下载最终生成的文件

### 3. API 调用

#### 获取可用的链类型

```bash
curl http://localhost:8001/api/prompt-chaining/types
```

#### 运行提示链（非流式）

```bash
curl -X POST http://localhost:8001/api/prompt-chaining/run \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Python 异步编程入门",
    "chain_type": "document_gen",
    "save_result": true
  }'
```

#### 运行提示链（流式）

```bash
curl -X POST http://localhost:8001/api/prompt-chaining/run/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Python 异步编程入门",
    "chain_type": "document_gen",
    "save_result": true
  }'
```

## 🔧 代码使用

### 基础用法

```python
from src.shuyixiao_agent.gitee_ai_client import GiteeAIClient
from src.shuyixiao_agent.agents.prompt_chaining_agent import (
    PromptChainingAgent,
    ChainStep
)

# 1. 初始化
llm_client = GiteeAIClient()
agent = PromptChainingAgent(llm_client, verbose=True)

# 2. 定义提示链步骤
steps = [
    ChainStep(
        name="步骤1",
        description="这是第一步",
        prompt_template="请分析：{input}"
    ),
    ChainStep(
        name="步骤2",
        description="这是第二步",
        prompt_template="基于分析结果，提出方案：{input}"
    )
]

# 3. 创建并运行链
agent.create_chain("my_chain", steps)
result = agent.run_chain("my_chain", "如何提高代码质量？")

# 4. 获取结果
if result.success:
    print(result.final_output)
    print(f"总耗时: {result.execution_time:.2f}秒")
```

### 使用预定义的链

```python
from src.shuyixiao_agent.agents.prompt_chaining_agent import (
    PromptChainingAgent,
    DocumentGenerationChain
)

# 使用文档生成链
agent = PromptChainingAgent(llm_client)
agent.create_chain("doc_gen", DocumentGenerationChain.get_steps())
result = agent.run_chain("doc_gen", "Docker 容器化实践")

# 保存结果
with open("document.md", 'w', encoding='utf-8') as f:
    f.write(result.final_output)
```

### 自定义转换函数

```python
def extract_summary(text: str) -> str:
    """提取摘要"""
    lines = text.split('\n')
    return '\n'.join(lines[:3])  # 只保留前3行

steps = [
    ChainStep(
        name="生成内容",
        prompt_template="写一篇关于{input}的文章",
    ),
    ChainStep(
        name="提取摘要",
        prompt_template="为以下内容生成摘要：{input}",
        transform_fn=extract_summary  # 应用自定义转换
    )
]
```

## 📊 查看执行过程

Prompt Chaining Agent 支持详细的执行追踪：

```python
# 启用 verbose 模式
agent = PromptChainingAgent(llm_client, verbose=True)

result = agent.run_chain("my_chain", "输入内容")

# 查看中间结果
for step_result in result.intermediate_results:
    print(f"\n步骤 {step_result['step']}: {step_result['name']}")
    print(f"输出: {step_result['output'][:100]}...")
```

## 🎯 最佳实践

### 1. 设计清晰的步骤

每个步骤应该：
- 有明确的单一职责
- 输入输出清晰
- 提示词具体明确

❌ 不好的设计：
```python
ChainStep(
    name="处理",
    prompt_template="处理这个：{input}"  # 太模糊
)
```

✅ 好的设计：
```python
ChainStep(
    name="提取关键信息",
    description="从文本中提取关键实体和关系",
    prompt_template="""请从以下文本中提取：
1. 关键实体（人名、地名、组织等）
2. 实体间的关系
3. 重要时间节点

文本：{input}"""
)
```

### 2. 合理的步骤数量

- **2-3步**：适合简单任务（翻译、总结）
- **4-5步**：适合中等复杂度（文档生成、代码审查）
- **6+步**：适合复杂任务（研究规划、产品设计）

过多步骤会增加：
- 执行时间
- 错误传播风险
- API 调用成本

### 3. 处理错误

```python
result = agent.run_chain("my_chain", input_text)

if not result.success:
    print(f"执行失败: {result.error_message}")
    
    # 查看哪一步失败了
    print(f"已完成 {len(result.intermediate_results)} 步")
    
    # 获取最后成功的步骤输出
    if result.intermediate_results:
        last_step = result.intermediate_results[-1]
        print(f"最后成功的步骤: {last_step['name']}")
```

### 4. 优化提示词

提示词应该：
- **具体明确** - 清楚说明要做什么
- **包含上下文** - 说明前一步的输出代表什么
- **设定期望** - 明确输出格式和内容要求

示例：
```python
ChainStep(
    name="优化代码",
    prompt_template="""你是一位资深的 Python 开发专家。
    
前一步已经识别出以下代码问题：
{input}

请针对每个问题：
1. 提供具体的修改建议
2. 给出优化后的代码示例
3. 说明改进的理由和预期效果

请用 Markdown 格式输出，包含代码块。"""
)
```

## 🔄 与其他 Agent 的对比

| 特性 | Simple Agent | Tool Agent | RAG Agent | Prompt Chaining |
|------|--------------|------------|-----------|----------------|
| 复杂度 | 低 | 中 | 中-高 | 中 |
| 可控性 | 中 | 中 | 低 | **高** |
| 输出质量 | 中 | 中-高 | 高 | **高** |
| 适用场景 | 简单对话 | 工具调用 | 知识查询 | **复杂流程** |
| 可调试性 | 低 | 中 | 低 | **高** |

## 💡 实际应用案例

### 案例1：自动生成 API 文档

```python
steps = [
    ChainStep(name="分析代码", 
             prompt_template="分析这个 API 的功能：{input}"),
    ChainStep(name="生成接口说明",
             prompt_template="为以下 API 生成接口说明：{input}"),
    ChainStep(name="添加示例",
             prompt_template="为 API 文档添加使用示例：{input}"),
    ChainStep(name="生成错误码表",
             prompt_template="生成错误码说明表：{input}")
]
```

### 案例2：内容本地化

```python
steps = [
    ChainStep(name="翻译",
             prompt_template="将以下英文翻译成中文：{input}"),
    ChainStep(name="文化适配",
             prompt_template="调整内容以适应中文读者习惯：{input}"),
    ChainStep(name="术语统一",
             prompt_template="统一技术术语翻译：{input}")
]
```

### 案例3：数据分析报告

```python
steps = [
    ChainStep(name="数据理解",
             prompt_template="分析数据集特征：{input}"),
    ChainStep(name="识别模式",
             prompt_template="识别数据中的模式和趋势：{input}"),
    ChainStep(name="生成洞察",
             prompt_template="基于模式生成业务洞察：{input}"),
    ChainStep(name="提出建议",
             prompt_template="基于洞察提出行动建议：{input}")
]
```

## 🚀 高级功能

### 动态链构建

根据输入动态选择步骤：

```python
def create_adaptive_chain(complexity: str):
    base_steps = [
        ChainStep(name="理解", prompt_template="理解问题：{input}")
    ]
    
    if complexity == "high":
        base_steps.extend([
            ChainStep(name="分解", prompt_template="分解问题：{input}"),
            ChainStep(name="深度分析", prompt_template="深度分析：{input}")
        ])
    
    base_steps.append(
        ChainStep(name="总结", prompt_template="总结方案：{input}")
    )
    
    return base_steps
```

### 链的组合

将多个链串联起来：

```python
# 第一条链：内容生成
gen_result = agent.run_chain("content_gen", topic)

# 第二条链：质量检查
check_result = agent.run_chain("quality_check", gen_result.final_output)

# 第三条链：优化改进
final_result = agent.run_chain("optimize", check_result.final_output)
```

### 保存和复用链结果

```python
# 保存完整的执行记录
agent.save_chain_result(result, "result.json")

# 后续可以加载查看
import json
with open("result.json", 'r') as f:
    saved_result = json.load(f)
    
# 查看某一步的输出
step_2_output = saved_result['intermediate_results'][1]['output']
```

## 🎓 学习资源

- **原理文章**: [Agentic Design Patterns - Prompt Chaining](https://github.com/ginobefun/agentic-design-patterns-cn/blob/main/07-Chapter-01-Prompt-Chaining.md)
- **示例代码**: `examples/10_prompt_chaining_demo.py`
- **简单示例**: `examples/11_prompt_chaining_simple.py`
- **核心实现**: `src/shuyixiao_agent/agents/prompt_chaining_agent.py`

## 🤝 贡献

欢迎贡献更多实用的提示链场景！

如果你创建了有用的提示链，可以：
1. 在 `prompt_chaining_agent.py` 中添加新的 Chain 类
2. 在演示脚本中添加对应的场景
3. 提交 Pull Request

## 📝 常见问题

**Q: 提示链和普通的多轮对话有什么区别？**

A: 提示链的每一步都有专门设计的提示词，更专注和可控。普通多轮对话的提示词通常是通用的。

**Q: 如何选择合适的步骤数量？**

A: 根据任务复杂度和每步的明确性。如果一步能清楚表达，就不要分成两步。

**Q: 可以跳过某些步骤吗？**

A: 当前实现是顺序执行。如需条件跳转，可以使用转换函数来实现。

**Q: 如何处理步骤失败？**

A: 检查 `result.success` 和 `result.intermediate_results`，可以从失败的步骤重新开始。

**Q: API 调用成本如何？**

A: 每个步骤调用一次 LLM，成本 = 步骤数 × 单次调用成本。建议先用较小的输入测试。

## 🎉 开始使用

现在就试试吧！

```bash
# 快速体验
python examples/11_prompt_chaining_simple.py

# 完整功能
python examples/10_prompt_chaining_demo.py

# Web 界面
python run_web.py
```

享受 Prompt Chaining 带来的强大能力！🚀

