# Web 服务器故障排除指南

## 问题描述

启动 Web 服务器后无法访问的常见问题和解决方案。

## 快速诊断

### 步骤 1: 使用修复版启动脚本

我们提供了一个增强版的启动脚本，包含完整的诊断功能：

```bash
python run_web_fixed.py
```

这个脚本会：
- ✅ 检查所有依赖是否安装
- ✅ 测试应用是否可以正常导入
- ✅ 禁用 reload 模式以避免问题
- ✅ 增加超时时间
- ✅ 显示详细的启动日志

### 步骤 2: 测试服务器连接

在新的终端窗口运行测试脚本：

```bash
python test_server.py
```

这会测试：
- 主页 (/)
- 健康检查接口 (/api/health)
- API 文档 (/docs)

## 常见问题和解决方案

### 问题 1: 连接超时

**症状：**
```
HTTPConnectionPool(host='localhost', port=8000): Read timed out.
```

**可能原因：**
1. 首次启动时下载嵌入模型
2. 某些初始化组件阻塞
3. 防火墙阻止连接

**解决方案：**

#### 方案 A: 使用修复版启动脚本
```bash
python run_web_fixed.py
```

#### 方案 B: 禁用 RAG 功能（如果不需要）
编辑 `src/shuyixiao_agent/__init__.py`，注释掉 RAG 相关导入：
```python
# from .rag.rag_agent import RAGAgent  # 暂时禁用
```

#### 方案 C: 增加浏览器超时时间
等待 1-2 分钟，首次启动可能需要下载模型。

#### 方案 D: 检查防火墙
Windows 防火墙可能阻止访问，尝试：
1. 临时关闭防火墙测试
2. 或添加 Python 到防火墙白名单

### 问题 2: 端口被占用

**症状：**
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次
```

**解决方案：**

#### 方案 A: 查找并关闭占用端口的程序
```powershell
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000

# 结束进程（替换 PID 为实际进程 ID）
taskkill /PID <PID> /F
```

#### 方案 B: 使用其他端口
修改 `run_web_fixed.py` 中的端口号：
```python
uvicorn.run(
    "shuyixiao_agent.web_app:app",
    host="0.0.0.0",
    port=8001,  # 改为其他端口
    ...
)
```

### 问题 3: 模块未安装

**症状：**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**解决方案：**

确保在虚拟环境中安装了所有依赖：

```bash
# 激活虚拟环境（如果使用）
# Windows PowerShell
.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
# 或使用 poetry
poetry install
```

### 问题 4: API Key 未配置

**症状：**
启动日志显示 `API Key 已配置: False`

**解决方案：**

创建 `.env` 文件：
```bash
# 复制示例文件
copy env.example .env

# 编辑 .env 文件，添加你的 API Key
# GITEE_AI_API_KEY=你的API密钥
```

或在 PowerShell 中设置环境变量：
```powershell
$env:GITEE_AI_API_KEY="你的API密钥"
python run_web_fixed.py
```

### 问题 5: 浏览器显示无法连接

**症状：**
浏览器显示 "无法访问此网站" 或 "连接被拒绝"

**解决方案：**

#### 方案 A: 检查服务器是否真的在运行
查看终端窗口是否显示：
```
INFO:     Application startup complete.
```

#### 方案 B: 尝试不同的地址
- `http://localhost:8000`
- `http://127.0.0.1:8000`
- `http://0.0.0.0:8000`

#### 方案 C: 清除浏览器缓存
1. 按 Ctrl+Shift+Delete
2. 清除缓存
3. 刷新页面

#### 方案 D: 使用无痕模式
有时浏览器扩展会干扰连接，使用无痕模式测试。

## 诊断命令汇总

```bash
# 1. 使用修复版启动（推荐）
python run_web_fixed.py

# 2. 测试服务器连接
python test_server.py

# 3. 诊断模块导入
python diagnose_issue.py

# 4. 检查端口占用
netstat -ano | findstr :8000

# 5. 查看虚拟环境中的包
pip list | findstr pydantic
```

## 优化建议

### 1. 首次启动优化

首次启动可能需要下载嵌入模型，建议：

```python
# 预先下载模型
from sentence_transformers import SentenceTransformer

# 这会下载模型到缓存目录
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
print("模型下载完成！")
```

### 2. 配置优化

在 `.env` 文件中：
```env
# 使用 CPU 而不是等待 CUDA
EMBEDDING_DEVICE=cpu

# 减少超时时间
REQUEST_TIMEOUT=30
```

### 3. 生产环境配置

生产环境建议：
```python
# 禁用 reload
reload=False

# 增加 workers
workers=4

# 使用生产级 ASGI 服务器
# 例如 gunicorn + uvicorn worker
```

## 仍然无法解决？

如果以上方案都无法解决问题，请提供以下信息：

1. **完整的错误信息**
   ```bash
   python run_web_fixed.py 2>&1 | Out-File -FilePath error.log
   ```

2. **环境信息**
   ```bash
   python --version
   pip list > packages.txt
   ```

3. **测试结果**
   ```bash
   python test_server.py > test_result.txt
   ```

4. **端口状态**
   ```bash
   netstat -ano | findstr :8000 > port_status.txt
   ```

然后将这些文件提供给技术支持。

## 成功启动的标志

当服务器成功启动并可以访问时，你应该看到：

1. **终端输出：**
```
============================================================
✅ ShuYixiao Agent Web 应用已启动
============================================================
API Key 已配置: True
使用模型: DeepSeek-V3
============================================================
INFO:     Application startup complete.
```

2. **浏览器：**
   - 访问 http://localhost:8000 看到漂亮的 Web 界面
   - 可以进行对话

3. **测试脚本输出：**
```
[成功] 状态码: 200
[成功] HTML 内容正确
```

## 快速参考

| 问题 | 命令 |
|------|------|
| 启动服务器 | `python run_web_fixed.py` |
| 测试连接 | `python test_server.py` |
| 检查端口 | `netstat -ano \| findstr :8000` |
| 安装依赖 | `pip install -r requirements.txt` |
| 激活虚拟环境 | `.venv\Scripts\Activate.ps1` |

祝你使用愉快！🚀

