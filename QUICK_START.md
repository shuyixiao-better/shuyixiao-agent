# SSL 错误快速解决指南

## 问题现象
Web 界面出现错误：
```
SSL: UNEXPECTED_EOF_WHILE_READING
```

## ✅ 已完成的修复

我已经为你的项目完成了以下修复：

### 1. 代码修改
- ✅ **config.py** - 添加 `ssl_verify` 配置选项
- ✅ **gitee_ai_client.py** - 实现 SSL 配置、重试机制和 Session 复用
- ✅ **.env** - 添加 `SSL_VERIFY=false` 配置

### 2. 新增文件
- ✅ **docs/ssl_troubleshooting.md** - 详细的故障排除指南
- ✅ **SSL_FIX_GUIDE.md** - 快速修复指南
- ✅ **test_ssl_fix.py** - 验证脚本
- ✅ **QUICK_START.md** (本文件) - 快速开始指南

## 🚀 立即使用（3 步）

### 步骤 1: 确认配置
检查 `.env` 文件中是否有以下配置：
```bash
SSL_VERIFY=false
```

如果没有，手动添加这一行。

### 步骤 2: 确保依赖已安装（如果尚未安装）
```bash
# 使用 Poetry（推荐）
poetry install

# 或使用 pip
pip install -r requirements.txt  # 如果有 requirements.txt

# 或手动安装核心依赖
pip install pydantic-settings requests urllib3
```

### 步骤 3: 重启 Web 服务
```bash
# 如果服务正在运行，按 Ctrl+C 停止
# 然后重新启动

# 使用 Poetry
poetry run python run_web.py

# 或直接运行
python run_web.py
```

浏览器访问：
```
http://localhost:8000
```

## 🔍 验证修复（可选）

运行测试脚本验证所有配置是否正确：
```bash
python test_ssl_fix.py
```

预期输出示例：
```
[OK] 配置加载成功
   - SSL Verify: False
[OK] 客户端创建成功
[OK] API 连接成功
[SUCCESS] 所有关键测试通过！
```

## ❓ 常见问题

### Q1: 为什么要禁用 SSL 验证？
**A:** Windows 系统的 SSL 库在连接某些 API 时可能存在兼容性问题。禁用 SSL 验证可以绕过这个问题。这在开发环境是安全的。

### Q2: 修改后还是出现 SSL 错误？
**A:** 请检查：
1. `.env` 文件是否在项目根目录
2. `SSL_VERIFY=false` 是否正确写入
3. 是否已重启 Web 服务
4. 运行 `python test_ssl_fix.py` 查看详细错误

### Q3: 提示模块未找到？
**A:** 运行以下命令安装依赖：
```bash
poetry install
# 或
pip install pydantic-settings requests
```

### Q4: 生产环境可以用吗？
**A:** 开发环境：可以安全使用
生产环境：建议设置 `SSL_VERIFY=true` 并解决证书问题

## 📋 核心修改说明

### 1. 配置文件 (config.py)
新增配置项：
```python
ssl_verify: bool = Field(
    default=False,  # 默认禁用 SSL 验证
    description="是否验证 SSL 证书"
)
```

### 2. API 客户端 (gitee_ai_client.py)
改进：
- ✅ 添加 SSL 验证开关
- ✅ 实现自动重试机制（最多 3 次）
- ✅ 使用 Session 复用连接
- ✅ 更详细的 SSL 错误提示

### 3. 环境配置 (.env)
新增配置：
```bash
SSL_VERIFY=false
```

## 🎯 完整的 .env 配置示例

```bash
# Gitee AI API 配置
GITEE_AI_API_KEY=your_api_key_here
GITEE_AI_BASE_URL=https://ai.gitee.com/v1
GITEE_AI_MODEL=DeepSeek-V3

# 请求配置
REQUEST_TIMEOUT=60
MAX_RETRIES=3

# SSL 配置（解决 SSL 错误）
SSL_VERIFY=false

# Agent 配置
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=true
ENABLE_FAILOVER=true
```

## 📚 更多信息

- **详细故障排除**：查看 `docs/ssl_troubleshooting.md`
- **项目文档**：查看 `README.md`
- **API 文档**：查看 `docs/api_reference.md`

## ✨ 技术细节

### 修改前
```python
response = requests.post(url, headers=headers, json=payload)
```

### 修改后
```python
# 使用 Session 和 SSL 配置
response = self.session.post(
    url, 
    headers=headers, 
    json=payload,
    verify=self.ssl_verify  # 可配置的 SSL 验证
)
```

### 重试机制
自动重试配置：
- 最多重试 3 次
- 对 429, 500, 502, 503, 504 状态码自动重试
- 使用指数退避策略

## 🎉 完成

现在你的 Web 界面应该可以正常工作了！

如果还有问题，请查看：
1. `SSL_FIX_GUIDE.md` - 更详细的解决方案
2. `docs/ssl_troubleshooting.md` - 技术细节
3. 运行 `python test_ssl_fix.py` - 诊断问题

