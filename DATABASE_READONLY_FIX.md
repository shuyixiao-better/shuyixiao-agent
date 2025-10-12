# 🔧 数据库只读错误修复指南

## ❌ 错误信息

```
Database error: error returned from database: (code: 1032) 
attempt to write a readonly database
```

## 🎯 问题原因

ChromaDB 的 SQLite 数据库文件没有写入权限，可能是因为：
1. 文件权限不正确
2. 目录权限不正确  
3. 磁盘空间不足
4. 数据库文件被其他进程锁定

---

## 💡 解决方案

### 方案 1：修复权限（推荐，无数据丢失）

```bash
# 1. 停止 Web 服务器（如果正在运行）
# 按 Ctrl+C 停止

# 2. 进入项目目录
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent

# 3. 运行修复脚本
bash fix_database_permissions.sh

# 4. 重新启动服务器
python run_web.py
```

### 方案 2：重置数据库（⚠️ 会清空所有数据）

如果方案 1 不work，可以尝试完全重置：

```bash
# 1. 停止 Web 服务器

# 2. 运行重置脚本
bash reset_database.sh

# 3. 输入 YES 确认

# 4. 重新启动服务器
python run_web.py

# 5. 重新上传文档
```

### 方案 3：手动修复

```bash
# 1. 确保目录存在
mkdir -p data/chroma

# 2. 修复目录权限
chmod 755 data/chroma

# 3. 如果数据库文件存在，修复文件权限
chmod 644 data/chroma/*.sqlite3 2>/dev/null || true
chmod 644 data/chroma/*.db 2>/dev/null || true

# 4. 修复所有子目录权限
find data/chroma -type d -exec chmod 755 {} \;
find data/chroma -type f -exec chmod 644 {} \;

# 5. 检查当前用户对目录的权限
ls -la data/chroma

# 6. 重新启动服务器
python run_web.py
```

---

## 🔍 诊断问题

### 检查磁盘空间

```bash
df -h .
```

如果磁盘空间不足（使用率 > 95%），需要清理空间。

### 检查文件权限

```bash
ls -la data/chroma/
```

应该看到类似这样的输出：
```
drwxr-xr-x  2 shuyixiao  staff    64 Oct 13 00:35 .
-rw-r--r--  1 shuyixiao  staff  1024 Oct 13 00:35 chroma.sqlite3
```

### 检查进程占用

```bash
# 检查是否有其他进程占用数据库
lsof data/chroma/chroma.sqlite3 2>/dev/null || echo "无进程占用"
```

如果有进程占用，先停止那些进程。

---

## 🚀 完整操作步骤

### 步骤 1：停止服务器

如果 Web 服务器正在运行，按 `Ctrl+C` 停止。

### 步骤 2：执行修复

```bash
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent
bash fix_database_permissions.sh
```

### 步骤 3：验证修复

```bash
# 查看目录权限
ls -la data/chroma/

# 应该看到：
# drwxr-xr-x (755) - 目录可读写执行
# -rw-r--r-- (644) - 文件可读写
```

### 步骤 4：启动服务器

```bash
# 使用虚拟环境（如果有）
source .venv/bin/activate

# 启动服务器
python run_web.py
```

### 步骤 5：测试

1. 访问 http://localhost:8000
2. 进入 "知识库管理" 标签
3. 尝试上传文本
4. 应该看到成功消息

---

## 🐛 如果仍然失败

### 检查 1：确认数据库路径

```bash
# 查找所有 chroma 数据库文件
find ~ -name "chroma.sqlite3" -type f 2>/dev/null | head -10
```

如果找到多个数据库文件，可能是路径配置问题。

### 检查 2：查看详细错误

启动服务器后，查看控制台的完整错误堆栈。

### 检查 3：检查配置文件

编辑 `src/shuyixiao_agent/config.py`：

```python
vector_db_path: str = Field(
    default="./data/chroma",  # 确认这个路径
    description="向量数据库存储路径"
)
```

确保路径正确。

### 检查 4：使用诊断脚本

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行诊断
python3 diagnose_database.py
```

---

## 📝 预防措施

### 1. 确保正确的启动方式

```bash
# 始终在项目根目录启动
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent

# 使用虚拟环境
source .venv/bin/activate

# 启动服务器
python run_web.py
```

### 2. 定期备份数据库

```bash
# 创建备份
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz data/chroma/

# 查看备份
ls -lh chroma_backup_*.tar.gz
```

### 3. 监控磁盘空间

```bash
# 定期检查
df -h | grep "/$"
```

确保至少有 1GB 可用空间。

---

## 🆘 紧急恢复

如果所有方法都失败，使用此紧急方案：

```bash
# 1. 完全删除数据库
rm -rf data/chroma/

# 2. 重新创建目录
mkdir -p data/chroma
chmod 755 data/chroma

# 3. 重启服务器
python run_web.py

# 4. 重新上传所有文档
```

⚠️ **注意**：此操作会丢失所有知识库数据！

---

## ✅ 验证修复成功

修复成功后，你应该能够：

1. ✅ 上传文本到知识库（无错误）
2. ✅ 查看文档列表
3. ✅ 删除文档
4. ✅ 查询 RAG
5. ✅ 在 `data/chroma/` 目录看到数据库文件

---

## 📞 获取帮助

如果以上方法都无法解决，请提供以下信息：

1. 完整的错误堆栈
2. `ls -la data/chroma/` 的输出
3. `df -h` 的输出
4. Python 版本：`python --version`
5. 操作系统版本：`sw_vers`

---

## 🔗 相关文档

- [RAG 存储位置说明](RAG_STORAGE_GUIDE.md)
- [文档管理功能指南](DOCUMENT_MANAGEMENT_GUIDE.md)
- [快速开始](QUICK_START.md)

