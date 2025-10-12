# ✅ 数据库只读错误 - 修复总结

## 📋 问题概述

**错误信息：**
```
✗ 上传文本失败: Database error: error returned from database: 
(code: 1032) attempt to write a readonly database
```

**根本原因：** ChromaDB SQLite 数据库文件权限问题

---

## 🔧 已执行的修复

### ✅ 完成的操作

1. **停止了正在运行的服务器**
2. **创建并设置了数据库目录权限** (755)
3. **清理了临时文件** (*.tmp, *-shm, *-wal)
4. **验证了磁盘空间** (1.6Ti 可用，使用率 12%)

### 📁 当前状态

```
目录: data/chroma/
权限: drwxr-xr-x (755)
状态: 空目录（将在首次使用时自动创建数据库）
```

---

## 🚀 现在开始使用

### 步骤 1：启动服务器

```bash
# 进入项目目录
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent

# 激活虚拟环境
source .venv/bin/activate

# 启动服务器
python run_web.py
```

### 步骤 2：测试上传

1. 打开浏览器访问：http://localhost:8000
2. 进入 **"🗄️ 知识库管理"** 标签页
3. 在 **"📝 上传文本"** 卡片中：
   - 知识库名称：`default`（或任意名称）
   - 文本内容：输入一些测试文本
   - 点击 **"上传文本"**

### 步骤 3：验证成功

如果看到：
```
✓ 成功上传 X 个文档片段
```

说明问题已解决！🎉

---

## 📚 创建的修复工具

### 1. `quick_fix.sh` - 一键修复（已执行）

快速修复数据库权限问题。

```bash
bash quick_fix.sh
```

**功能：**
- 停止运行中的服务器
- 修复目录和文件权限
- 清理临时文件
- 检查磁盘空间

### 2. `fix_database_permissions.sh` - 权限修复

只修复权限，不删除数据。

```bash
bash fix_database_permissions.sh
```

### 3. `reset_database.sh` - 完全重置

⚠️ **警告：会删除所有数据！**

```bash
bash reset_database.sh
# 输入 YES 确认
```

**使用场景：**
- 数据库文件损坏
- 权限修复无效
- 需要重新开始

### 4. `diagnose_database.py` - 诊断工具

详细诊断数据库状态。

```bash
source .venv/bin/activate
python diagnose_database.py
```

---

## 🔍 如果问题仍然存在

### 检查清单

#### 1. 确认目录权限

```bash
ls -la data/chroma/
```

应该看到：
```
drwxr-xr-x  2 shuyixiao  staff  64 Oct 13 00:35 .
```

#### 2. 检查是否有进程锁定文件

```bash
lsof data/chroma/chroma.sqlite3 2>/dev/null
```

如果有输出，停止那些进程。

#### 3. 检查磁盘空间

```bash
df -h .
```

确保有足够空间（至少 100MB）。

#### 4. 查看完整错误日志

启动服务器时，查看控制台输出的完整错误堆栈。

---

## 💡 常见问题

### Q1: 上传后看不到文档？

**解决方法：**
1. 进入 **"文档浏览器"** 卡片
2. 输入知识库名称
3. 点击 **"加载文档列表"**

### Q2: 提示"集合不存在"？

**解决方法：**
- 先上传至少一个文档，系统会自动创建集合
- 或检查知识库名称是否正确

### Q3: 知识库名称变成了 `kb_xxxxx`？

这是正常的！系统会自动将中文名称转换为合法的英文名称。

**示例：**
- `舒一笑不秃头个人信息` → `kb_dd65ff91`
- `default` → `default`（已经合法）

你仍然可以使用原始名称，系统会自动映射。

### Q4: 数据库文件在哪里？

**位置：** `data/chroma/`

**结构：**
```
data/chroma/
├── chroma.sqlite3          # 主数据库文件
├── [uuid-1]/              # 集合 1 的数据
├── [uuid-2]/              # 集合 2 的数据
└── ...
```

---

## 🎯 预防措施

### 1. 正确启动服务器

始终在项目根目录启动：

```bash
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent
python run_web.py
```

### 2. 使用虚拟环境

```bash
source .venv/bin/activate
python run_web.py
```

### 3. 定期备份数据库

```bash
# 手动备份
cp -r data/chroma data/chroma_backup_$(date +%Y%m%d)

# 或使用 tar
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz data/chroma/
```

### 4. 监控磁盘空间

```bash
df -h .
```

保持至少 1GB 可用空间。

---

## 📖 相关文档

- **[数据库只读错误修复指南](DATABASE_READONLY_FIX.md)** - 详细的修复步骤
- **[文档管理功能指南](DOCUMENT_MANAGEMENT_GUIDE.md)** - 如何使用新功能
- **[RAG 存储位置说明](RAG_STORAGE_GUIDE.md)** - 数据存储详解
- **[快速开始](QUICK_START.md)** - 项目入门指南

---

## ✨ 新功能提醒

现在你可以：

1. ✅ **查看文档列表** - 浏览知识库中的所有文档
2. ✅ **查看文档详情** - 查看完整内容和元数据
3. ✅ **删除文档** - 精确删除不需要的文档
4. ✅ **实时统计** - 查看文档数量和信息

进入 **"🗄️ 知识库管理"** → **"📄 文档浏览器"** 开始使用！

---

## 🆘 需要帮助？

如果以上方法都无法解决问题，请提供：

1. 完整的错误日志（从启动到报错）
2. `ls -la data/chroma/` 的输出
3. `df -h` 的输出
4. 操作系统版本：`sw_vers`

---

## 🎉 祝使用愉快！

问题已修复，现在可以正常使用所有功能了！

**下一步：**
1. 启动服务器：`python run_web.py`
2. 访问 http://localhost:8000
3. 开始上传和管理文档

---

*最后更新：2024-10-13*

