# 🚀 快速开始 - 数据库已配置完成

## ✅ 配置已完成

数据库路径已固定在项目目录中：
```
/Users/shuyixiao/PycharmProjects/shuyixiao-agent/data/chroma/
```

所有旧数据已清理，权限已修复，现在可以直接使用了！

---

## 🎯 立即开始（3步）

### 步骤 1：启动服务器

```bash
# 进入项目目录
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent

# 激活虚拟环境
source .venv/bin/activate

# 启动服务器
python run_web.py
```

看到这个提示说明启动成功：
```
✅ ShuYixiao Agent Web 应用已启动
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 步骤 2：访问界面

打开浏览器访问：**http://localhost:8000**

### 步骤 3：上传文档

1. 点击 **"🗄️ 知识库管理"** 标签页
2. 在 **"📝 上传文本"** 卡片中：
   - 知识库名称：输入 `my_knowledge`（或任意名称）
   - 文本内容：输入一些测试文本
   - 点击 **"上传文本"**
3. 看到 `✓ 成功上传 X 个文档片段` 说明成功！

---

## 🎨 功能预览

### 1️⃣ 智能对话
- 简单对话模式
- 工具调用模式
- 流式响应

### 2️⃣ RAG 问答
- 基于知识库的问答
- 混合检索（向量+关键词）
- 查询优化
- 对话历史支持

### 3️⃣ 知识库管理
- 📝 上传文本
- 📁 上传文件
- ℹ️ 查看信息
- 📄 浏览文档（新功能）
- 🗑️ 管理知识库

---

## 📄 文档浏览功能（新）

### 查看所有文档

1. 进入 **"知识库管理"** 标签页
2. 滚动到 **"📄 文档浏览器"** 卡片
3. 输入知识库名称
4. 点击 **"加载文档列表"**

### 查看文档详情

- 点击文档的 **"查看"** 按钮
- 在弹出的模态框中查看完整内容
- 可以查看文档的元数据（如果有）

### 删除文档

- **方式 1：** 在列表中点击 **"删除"** 按钮
- **方式 2：** 在详情模态框中点击 **"删除文档"**

---

## 🔍 验证数据位置

### 查看数据库文件

```bash
# 查看目录内容
ls -la /Users/shuyixiao/PycharmProjects/shuyixiao-agent/data/chroma/

# 查看数据库大小
du -sh /Users/shuyixiao/PycharmProjects/shuyixiao-agent/data/chroma/
```

### 验证配置

```bash
# 运行验证脚本
bash verify_simple.sh
```

应该看到：
```
✓ 项目根目录: /Users/shuyixiao/PycharmProjects/shuyixiao-agent
✓ 数据库路径: /Users/shuyixiao/PycharmProjects/shuyixiao-agent/data/chroma
✓ 是绝对路径: True
✓ 目录存在: True
✓ 在项目内: True
✅ 配置验证通过！
```

---

## 🛠️ 常用命令

### 启动服务器
```bash
cd /Users/shuyixiao/PycharmProjects/shuyixiao-agent
source .venv/bin/activate
python run_web.py
```

### 停止服务器
```bash
# 按 Ctrl+C
```

### 重启服务器
```bash
# 1. 停止服务器（Ctrl+C）
# 2. 重新启动
python run_web.py
```

### 清空所有数据（慎用）
```bash
bash reset_database.sh
# 输入 YES 确认
```

### 修复权限问题
```bash
bash fix_database_permissions.sh
```

### 备份数据
```bash
# 方式 1：简单备份
cp -r data/chroma data/chroma_backup_$(date +%Y%m%d)

# 方式 2：压缩备份
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz data/chroma/
```

---

## 📊 测试场景

建议测试以下场景：

### ✅ 基础测试
- [ ] 上传文本
- [ ] 上传文件
- [ ] 查询 RAG
- [ ] 查看文档列表
- [ ] 删除文档

### ✅ 高级测试
- [ ] 使用中文知识库名称
- [ ] 上传大量文档（100+）
- [ ] 测试混合检索
- [ ] 测试查询优化
- [ ] 测试对话历史

### ✅ 压力测试
- [ ] 连续上传多次
- [ ] 大文件上传
- [ ] 并发查询
- [ ] 长时间运行

---

## 🐛 常见问题

### Q1: 无法访问 http://localhost:8000

**解决方法：**
- 检查服务器是否启动（看控制台输出）
- 检查端口是否被占用：`lsof -i :8000`
- 尝试使用 http://127.0.0.1:8000

### Q2: 上传文本失败

**解决方法：**
```bash
# 1. 检查数据库权限
bash fix_database_permissions.sh

# 2. 重启服务器
# Ctrl+C 停止，然后重新启动

# 3. 如果仍失败，查看完整错误日志
```

### Q3: 找不到文档

**解决方法：**
- 确认知识库名称输入正确
- 点击 **"刷新"** 按钮
- 检查 **"知识库信息"** 确认文档数量

### Q4: 知识库名称变成了 `kb_xxxxx`

这是正常的！系统会自动将中文名称转换为合法名称：
- `我的知识库` → `kb_12345678`
- `default` → `default`（已经合法）

你仍然可以使用原始名称，系统会自动映射。

---

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| [DATABASE_PATH_UPDATED.md](DATABASE_PATH_UPDATED.md) | 数据库路径配置详解 |
| [DOCUMENT_MANAGEMENT_GUIDE.md](DOCUMENT_MANAGEMENT_GUIDE.md) | 文档管理功能指南 |
| [DATABASE_READONLY_FIX.md](DATABASE_READONLY_FIX.md) | 数据库只读错误修复 |
| [RAG_STORAGE_GUIDE.md](RAG_STORAGE_GUIDE.md) | RAG 存储位置说明 |
| [README_FIX_SUMMARY.md](README_FIX_SUMMARY.md) | 修复总结 |

---

## 🎉 就是这样！

现在你可以：
- ✅ 上传和管理文档
- ✅ 进行 RAG 问答
- ✅ 浏览和删除文档
- ✅ 数据固定保存在项目目录中

**开始使用吧！** 🚀

如有问题，查看上面的常见问题或详细文档。

---

*最后更新：2024-10-13*

