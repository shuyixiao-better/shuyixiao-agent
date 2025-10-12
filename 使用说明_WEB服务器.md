# ShuYixiao Agent Web 服务器使用说明

## 🚀 快速启动

### 方法 1: 使用修复版启动脚本（推荐）

```bash
python run_web_fixed.py
```

**优点：**
- ✅ 自动检查依赖
- ✅ 更稳定，不会超时
- ✅ 详细的诊断信息

### 方法 2: 使用原始启动脚本

```bash
python run_web.py
```

## 📝 首次使用步骤

### 1. 确保在虚拟环境中

```powershell
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 你应该看到命令提示符前有 (shuyixiao-agent-py3.12)
```

### 2. 配置 API Key（可选但推荐）

创建 `.env` 文件：
```env
GITEE_AI_API_KEY=你的API密钥
GITEE_AI_MODEL=DeepSeek-V3
GITEE_AI_BASE_URL=https://ai.gitee.com/v1
```

### 3. 启动服务器

```bash
python run_web_fixed.py
```

### 4. 访问 Web 界面

在浏览器中打开：
- **Web 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 🎯 功能说明

### 1. 智能对话
- **简单对话**：基础 AI 对话功能
- **工具调用**：可以使用各种工具（搜索、计算等）

### 2. RAG 问答
- 基于知识库的智能问答
- 支持混合检索、向量检索、关键词检索
- 可调整 Top K、查询优化等参数

### 3. 知识库管理
- **上传文本**：直接输入文本添加到知识库
- **上传文件**：从本地文件添加到知识库
- **查看信息**：查看知识库状态
- **清空知识库**：删除所有文档

## ⚡ 常见问题

### Q: 启动后浏览器无法访问？

**A**: 
1. 使用 `python run_web_fixed.py` 重新启动
2. 等待 1-2 分钟（首次启动可能需要下载模型）
3. 尝试访问 http://127.0.0.1:8000
4. 检查防火墙设置

### Q: 提示端口被占用？

**A**:
```powershell
# 查找占用端口的程序
netstat -ano | findstr :8000

# 结束该进程（替换 <PID> 为实际进程 ID）
taskkill /PID <PID> /F
```

### Q: 提示模块未安装？

**A**:
```bash
# 确保在虚拟环境中
.venv\Scripts\Activate.ps1

# 重新安装依赖
pip install -r requirements.txt
```

## 🔧 测试工具

### 测试服务器连接

```bash
python test_server.py
```

这会测试：
- ✅ 主页是否可访问
- ✅ API 是否正常
- ✅ 文档是否可用

### 诊断模块导入

```bash
python diagnose_issue.py
```

检查所有模块是否可以正常导入。

## 📊 性能说明

### 首次启动
- **时间**: 可能需要 1-3 分钟
- **原因**: 下载嵌入模型（约 100MB）
- **后续**: 启动会很快（几秒钟）

### 首次使用 RAG
- **时间**: 第一次查询可能需要 10-30 秒
- **原因**: 加载嵌入模型到内存
- **后续**: 查询会很快（1-2 秒）

## 🎨 界面说明

### 主界面标签页

1. **💬 智能对话**
   - 选择 Agent 类型
   - 输入问题
   - 查看回复

2. **📚 RAG 问答**
   - 选择知识库
   - 配置检索参数
   - 基于文档回答

3. **🗄️ 知识库管理**
   - 上传文档
   - 查看统计
   - 管理知识库

## 🔐 安全提示

### 开发环境
```env
# .env 文件不要提交到 git
GITEE_AI_API_KEY=你的密钥
```

### 生产环境
- 修改 CORS 设置
- 使用 HTTPS
- 添加身份验证
- 限制访问来源

```python
# 修改 web_app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # 指定域名
    ...
)
```

## 📚 更多帮助

- **故障排除指南**: 查看 `WEB_SERVER_TROUBLESHOOTING.md`
- **API 参考**: 访问 http://localhost:8000/docs
- **项目文档**: 查看 `docs/` 目录

## 🎉 成功标志

服务器成功运行的标志：

1. **终端显示**:
```
✅ ShuYixiao Agent Web 应用已启动
INFO:     Application startup complete.
```

2. **浏览器**:
   - 看到漂亮的渐变色界面
   - 右上角显示 "在线" 状态
   - 可以正常对话

3. **测试通过**:
```bash
python test_server.py
# 所有测试显示 [成功]
```

---

**祝你使用愉快！如有问题，请查看故障排除指南。** 🚀

