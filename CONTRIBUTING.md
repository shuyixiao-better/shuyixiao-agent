# 贡献指南

感谢你考虑为 shuyixiao-agent 做出贡献！

## 行为准则

- 保持友好和尊重
- 接受建设性的批评
- 关注项目的最佳利益
- 对社区成员保持同理心

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请创建一个 Issue 并包含：

1. **清晰的标题**：简要描述问题
2. **复现步骤**：详细说明如何重现问题
3. **期望行为**：说明你期望发生什么
4. **实际行为**：说明实际发生了什么
5. **环境信息**：
   - Python 版本
   - 操作系统
   - 相关依赖版本
6. **代码示例**：如果可能，提供最小的复现代码

### 建议新功能

如果你有新功能的想法：

1. 创建一个 Issue 说明：
   - 功能描述
   - 使用场景
   - 可能的实现方式
2. 等待维护者反馈
3. 开始实现前先讨论设计

### 提交代码

#### 设置开发环境

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/your-username/shuyixiao-agent.git
cd shuyixiao-agent

# 2. 安装依赖（包括开发依赖）
poetry install --with dev

# 3. 激活虚拟环境
poetry shell

# 4. 创建新分支
git checkout -b feature/your-feature-name
```

#### 代码规范

1. **Python 风格**：
   - 遵循 PEP 8
   - 使用 Black 格式化代码
   - 使用 Ruff 进行 Lint

2. **类型提示**：
   - 为函数添加类型提示
   - 使用 mypy 进行类型检查

3. **文档字符串**：
   ```python
   def example_function(param: str) -> int:
       """
       函数的简短描述
       
       Args:
           param: 参数描述
           
       Returns:
           返回值描述
           
       Raises:
           ValueError: 错误描述
       """
       pass
   ```

4. **提交信息**：
   ```
   类型: 简短描述（不超过50字符）
   
   详细说明（如果需要）
   
   类型可以是：
   - feat: 新功能
   - fix: Bug 修复
   - docs: 文档更新
   - style: 代码格式（不影响功能）
   - refactor: 重构
   - test: 测试
   - chore: 构建过程或辅助工具的变动
   ```

#### 开发流程

```bash
# 1. 编写代码
# ... 进行修改 ...

# 2. 格式化代码
black src/ examples/

# 3. 运行 Lint
ruff check src/ examples/

# 4. 类型检查（可选）
mypy src/

# 5. 运行测试（如果有）
pytest

# 6. 提交更改
git add .
git commit -m "feat: add new feature"

# 7. 推送到你的 fork
git push origin feature/your-feature-name

# 8. 创建 Pull Request
```

#### Pull Request 检查清单

在提交 PR 前，请确保：

- [ ] 代码符合项目风格
- [ ] 已添加必要的文档
- [ ] 已添加或更新测试（如适用）
- [ ] 所有测试通过
- [ ] 提交信息清晰明确
- [ ] 已更新 CHANGELOG.md（如适用）

### 文档贡献

文档同样重要！你可以：

- 修正拼写或语法错误
- 改进现有文档的清晰度
- 添加新的示例
- 翻译文档

文档位于 `docs/` 目录，使用 Markdown 格式。

## 项目结构

```
shuyixiao-agent/
├── src/shuyixiao_agent/    # 主要代码
│   ├── agents/             # Agent 实现
│   ├── tools/              # 工具
│   ├── config.py           # 配置
│   └── gitee_ai_client.py  # API 客户端
├── examples/               # 示例代码
├── docs/                   # 文档
└── tests/                  # 测试（未来）
```

## 开发提示

### 添加新的 Agent

1. 在 `src/shuyixiao_agent/agents/` 创建新文件
2. 继承基类或实现 LangGraph 图
3. 在 `agents/__init__.py` 中导出
4. 添加示例到 `examples/`
5. 更新文档

### 添加新工具

1. 在 `src/shuyixiao_agent/tools/` 添加工具函数
2. 添加工具定义到 `TOOL_DEFINITIONS`
3. 在 `tools/__init__.py` 中导出
4. 添加使用示例
5. 更新文档

### 测试本地更改

```python
# 在项目根目录创建测试脚本
# test_my_changes.py

import sys
sys.path.insert(0, './src')

from shuyixiao_agent import SimpleAgent

agent = SimpleAgent()
print(agent.chat("测试"))
```

## 寻求帮助

如果你有任何问题：

1. 查看 [文档](docs/)
2. 搜索 [已有 Issues](https://github.com/your-username/shuyixiao-agent/issues)
3. 创建新的 Issue 提问

## 许可证

提交代码即表示你同意将你的贡献以项目的许可证（MIT）发布。

---

再次感谢你的贡献！🎉

