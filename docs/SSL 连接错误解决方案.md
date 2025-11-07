# SSL 连接错误解决方案

## 问题描述

当使用 Web 界面进行问答时，可能会遇到以下错误：

```
处理请求时出错: API 请求失败: HTTPSConnectionPool(host='ai.gitee.com', port=443): 
Max retries exceeded with url: /v1/chat/completions 
(Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] 
EOF occurred in violation of protocol (_ssl.c:1000)')))
```

这是一个常见的 SSL/TLS 握手错误，特别是在 Windows 系统上。

## 解决方案

### 方案一：禁用 SSL 证书验证（推荐，最快）

1. **创建或编辑 `.env` 文件**
   
   在项目根目录下，将 `env.example` 复制为 `.env`：
   ```bash
   copy env.example .env
   ```

2. **配置 SSL_VERIFY 参数**
   
   在 `.env` 文件中添加或修改以下配置：
   ```
   SSL_VERIFY=false
   ```

3. **重启 Web 服务**
   ```bash
   python run_web.py
   ```

### 方案二：更新 Python SSL 库

1. **更新 certifi 包**
   ```bash
   pip install --upgrade certifi
   ```

2. **更新 requests 和 urllib3**
   ```bash
   pip install --upgrade requests urllib3
   ```

3. **重启应用**

### 方案三：使用系统代理（如果在代理环境下）

如果你在使用代理，可以在 `.env` 文件中配置代理：

```bash
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

然后修改代码使用代理设置。

### 方案四：更新系统 CA 证书

#### Windows 系统
1. 打开 Windows Update
2. 检查并安装所有可用更新
3. 重启系统

#### 手动安装证书
1. 下载最新的 CA 证书包
2. 在 Python 中指定证书路径

## 验证修复

1. **检查配置**
   
   访问健康检查接口：
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **测试连接**
   
   在浏览器中打开：
   ```
   http://localhost:8000
   ```
   
   发送一条测试消息，验证是否正常工作。

## 技术说明

### 为什么会出现这个错误？

1. **Windows SSL 库版本问题**：Windows 系统的 OpenSSL 库可能与服务器的 SSL/TLS 配置不兼容
2. **证书验证问题**：本地证书存储可能过期或不完整
3. **网络环境**：某些网络环境（如企业网络）可能有特殊的 SSL 拦截配置

### 禁用 SSL 验证安全吗？

- ✅ **开发环境**：可以安全使用，方便调试
- ⚠️ **生产环境**：不推荐，应该解决根本原因
- 🔒 **替代方案**：如果长期使用，建议配置正确的证书验证

### 代码改进

我们在代码中添加了以下改进：

1. **SSL 配置选项**：可以通过环境变量控制 SSL 验证
2. **重试机制**：自动重试失败的请求
3. **更好的错误提示**：提供明确的解决方案建议
4. **Session 复用**：使用 requests.Session 提高性能

## 配置文件示例

完整的 `.env` 文件示例：

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

## 常见问题

### Q: 设置 SSL_VERIFY=false 后还是报错？

A: 请确保：
1. `.env` 文件在项目根目录
2. 已经重启了 Web 服务
3. 环境变量格式正确（没有多余的空格或引号）

### Q: 我不想禁用 SSL 验证，有其他办法吗？

A: 可以尝试：
1. 更新 Python 到最新版本
2. 使用 `pip install --upgrade certifi requests urllib3`
3. 配置自定义 CA 证书路径

### Q: 只在某些网络下出现这个问题？

A: 这可能是网络环境导致的，建议：
1. 检查是否有代理或防火墙
2. 尝试更换网络环境
3. 联系网络管理员

## 需要帮助？

如果以上方案都无法解决问题，请：

1. 查看完整的错误日志
2. 检查 Python 版本和依赖包版本
3. 在 GitHub Issues 中反馈问题

## 相关文件

- `src/shuyixiao_agent/config.py` - 配置管理
- `src/shuyixiao_agent/gitee_ai_client.py` - API 客户端
- `env.example` - 环境变量示例

