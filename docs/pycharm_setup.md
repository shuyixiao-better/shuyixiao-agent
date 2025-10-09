# PyCharm 环境变量配置指南

本文档介绍如何在 PyCharm 中配置 Shuyixiao Agent 所需的环境变量。

## 方法一：在 PyCharm 运行配置中设置环境变量（推荐）

### 步骤说明

1. **打开运行配置**
   - 点击菜单栏：`Run` -> `Edit Configurations...`
   - 或者点击右上角的运行配置下拉菜单，选择 `Edit Configurations...`

2. **选择或创建运行配置**
   - 如果已有 Python 运行配置，直接选择
   - 如果没有，点击左上角的 `+` 按钮，选择 `Python`

3. **配置环境变量**
   - 在配置面板中找到 `Environment variables` 字段
   - 点击右侧的文件夹图标 📁
   - 在弹出的对话框中点击 `+` 按钮添加变量

4. **添加必需的环境变量**

   **必填项：**
   ```
   名称: GITEE_AI_API_KEY
   值: 你的API密钥（从 https://ai.gitee.com/ 获取）
   ```

   **可选项（有默认值）：**
   ```
   名称: GITEE_AI_BASE_URL
   值: https://ai.gitee.com/v1
   
   名称: GITEE_AI_MODEL
   值: DeepSeek-V3
   
   名称: AGENT_MAX_ITERATIONS
   值: 10
   
   名称: AGENT_VERBOSE
   值: true
   
   名称: REQUEST_TIMEOUT
   值: 60
   
   名称: MAX_RETRIES
   值: 3
   
   名称: ENABLE_FAILOVER
   值: true
   ```

5. **保存配置**
   - 点击 `OK` 保存环境变量
   - 再次点击 `OK` 或 `Apply` 保存运行配置

### 快速添加方式

你也可以使用 "粘贴多个变量" 的功能：

1. 点击环境变量编辑框右侧的文件夹图标
2. 点击对话框底部的 `Paste` 按钮（粘贴图标）
3. 粘贴以下内容（记得替换实际的 API Key）：

```
GITEE_AI_API_KEY=你的API密钥
GITEE_AI_BASE_URL=https://ai.gitee.com/v1
GITEE_AI_MODEL=DeepSeek-V3
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=true
REQUEST_TIMEOUT=60
MAX_RETRIES=3
ENABLE_FAILOVER=true
```

## 方法二：使用 .env 文件

如果你不想每次都在 PyCharm 中配置，可以使用 `.env` 文件：

1. **创建 .env 文件**
   ```bash
   # 在项目根目录下
   cp .env.example .env
   ```

2. **编辑 .env 文件**
   - 打开 `.env` 文件
   - 修改 `GITEE_AI_API_KEY` 为你的实际 API 密钥
   - 根据需要修改其他配置项

3. **确保 .env 文件不被提交到 Git**
   - `.env` 文件应该已经在 `.gitignore` 中
   - 确认命令：`git check-ignore .env`（应该显示 `.env`）

## 方法三：设置系统环境变量

如果你希望在所有项目中使用相同的配置，可以设置系统环境变量：

### Windows

1. **打开系统属性**
   - 右键点击 `此电脑` -> `属性`
   - 点击 `高级系统设置`
   - 点击 `环境变量` 按钮

2. **添加用户变量**
   - 在 "用户变量" 区域点击 `新建`
   - 添加所需的环境变量

### macOS/Linux

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
export GITEE_AI_API_KEY="你的API密钥"
export GITEE_AI_BASE_URL="https://ai.gitee.com/v1"
export GITEE_AI_MODEL="DeepSeek-V3"
```

重新加载配置：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

## 验证配置

创建一个测试脚本 `test_config.py`：

```python
from src.shuyixiao_agent.config import settings

print("配置加载成功！")
print(f"API Key: {'已设置' if settings.gitee_ai_api_key else '未设置'}")
print(f"Base URL: {settings.gitee_ai_base_url}")
print(f"Model: {settings.gitee_ai_model}")
print(f"Max Iterations: {settings.agent_max_iterations}")
print(f"Verbose: {settings.agent_verbose}")
print(f"Request Timeout: {settings.request_timeout}")
print(f"Max Retries: {settings.max_retries}")
print(f"Enable Failover: {settings.enable_failover}")
```

在 PyCharm 中运行此脚本，确认所有配置都正确加载。

## 注意事项

1. **环境变量名称不区分大小写**
   - `GITEE_AI_API_KEY` 和 `gitee_ai_api_key` 都可以识别
   - 但建议使用全大写格式（符合环境变量命名规范）

2. **配置优先级**
   - 系统环境变量（最高优先级）
   - PyCharm 运行配置中的环境变量
   - `.env` 文件
   - 代码中的默认值（最低优先级）

3. **安全建议**
   - 不要将 API 密钥提交到版本控制系统
   - 不要在代码中硬编码 API 密钥
   - 团队共享时使用 `.env.example` 作为模板

4. **调试技巧**
   - 如果配置没有生效，检查 PyCharm 的运行配置
   - 使用 `print(settings.dict())` 查看所有配置值
   - 确保 `.env` 文件在项目根目录

## 常见问题

### Q: 为什么我的 API Key 没有被读取？

A: 检查以下几点：
1. 环境变量名称是否正确（`GITEE_AI_API_KEY`）
2. PyCharm 运行配置是否已保存
3. 是否重新运行了程序（配置修改后需要重启）
4. `.env` 文件是否在项目根目录

### Q: 可以使用不同的配置运行不同的脚本吗？

A: 可以！在 PyCharm 中为每个脚本创建不同的运行配置，每个配置可以有不同的环境变量。

### Q: 如何在团队中共享配置？

A: 使用 `.env.example` 文件：
1. 团队成员复制 `.env.example` 为 `.env`
2. 每个人填入自己的 API 密钥
3. `.env.example` 提交到 Git，`.env` 不提交

## 相关文档

- [快速开始指南](getting_started.md)
- [API 参考文档](api_reference.md)
- [项目概览](PROJECT_OVERVIEW.md)

