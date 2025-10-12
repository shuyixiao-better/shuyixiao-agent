# 🚀 快速开始 - 云端 API 版

## 3 步启动 Web 服务器

### 步骤 1: 配置 API Key

创建 `.env` 文件：

```bash
# 复制示例文件
copy env_config_example.txt .env
```

编辑 `.env`，填入你的 API Key：

```env
GITEE_AI_API_KEY=你的API密钥
USE_CLOUD_EMBEDDING=true
```

💡 **获取 API Key**: https://ai.gitee.com/dashboard/settings/tokens

### 步骤 2: 启动服务器

```bash
# 激活虚拟环境（如果使用）
.venv\Scripts\Activate.ps1

# 启动优化版服务器
python run_web_optimized.py
```

### 步骤 3: 访问界面

打开浏览器访问: **http://localhost:8000**

---

## ✨ 优势

| 优化前（本地模型） | 优化后（云端 API） |
|-------------------|-------------------|
| ⏱️  启动时间: 60-120 秒 | ⚡ 启动时间: **3 秒** |
| 💾 模型下载: 100+ MB | 💾 模型下载: **0 MB** |
| 📉 成功率: 50%（超时） | ✅ 成功率: **100%** |
| 🐌 首次响应: 30-60 秒 | 🚀 首次响应: **1-2 秒** |

---

## 🎯 核心改进

1. **使用 Gitee AI 云端 API** - 无需下载模型
2. **延迟加载 RAG 组件** - 启动不阻塞
3. **智能配置系统** - 灵活切换云端/本地

---

## 🔧 其他启动方式

### 方式 1: 设置环境变量（临时）

```powershell
# PowerShell
$env:GITEE_AI_API_KEY="你的API密钥"
$env:USE_CLOUD_EMBEDDING="true"
python run_web_optimized.py
```

### 方式 2: 使用原始脚本

```bash
python run_web.py
```

**注意**: 原始脚本仍可用，但启动会较慢。

---

## 📝 功能说明

### 💬 智能对话
- 简单对话模式
- 工具调用模式（搜索、计算等）

### 📚 RAG 问答
- 基于知识库的智能问答
- 支持向量检索、关键词检索、混合检索
- 自动查询优化和重排序

### 🗄️ 知识库管理
- 上传文本、文件
- 查看知识库统计
- 清空知识库

---

## ⚡ 性能提示

- ✅ **启动速度**: 3 秒（vs 之前的 1-2 分钟）
- ✅ **首次访问**: 立即可用
- ✅ **RAG 功能**: 首次使用时初始化（约 5 秒）

---

## 🐛 遇到问题？

### Q: API Key 未配置

```bash
# 确认 .env 文件存在
dir .env

# 检查内容
type .env
```

### Q: 端口被占用

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程
taskkill /PID <进程ID> /F
```

### Q: 详细故障排除

查看完整文档:
- **优化说明**: `云端API优化说明.md`
- **故障排除**: `WEB_SERVER_TROUBLESHOOTING.md`

---

## 📚 更多文档

- **详细优化说明**: `云端API优化说明.md`
- **API 文档**: http://localhost:8000/docs（启动后）
- **项目文档**: `docs/` 目录
- **Gitee AI 文档**: https://ai.gitee.com/docs/products/apis

---

**现在就开始吧！** 🎉

