# 数据库持久化和权限问题修复方案

## 问题描述

1. **数据库只读错误**：项目重启后出现 `attempt to write a readonly database` 错误
2. **历史数据丢失**：重启后无法查询到之前上传的数据

## 根本原因

1. **权限问题**：ChromaDB 的 SQLite 数据库文件在某些情况下权限会被重置或不正确
2. **临时文件**：WAL（Write-Ahead Logging）和 SHM（Shared Memory）文件可能导致锁定
3. **目录权限**：`data/chroma` 目录权限不正确

## 解决方案

### 1. 自动权限修复（已实现）

新增 `database_helper.py` 模块，在应用启动时自动：
- 创建数据库目录（如果不存在）
- 设置正确的目录权限（755）
- 修复所有文件权限（644）
- 清理临时文件（*.tmp, *-shm, *-wal）

### 2. 启动时初始化（已集成）

在 `web_app.py` 的 `startup_event` 中集成数据库初始化：

```python
@app.on_event("startup")
async def startup_event():
    # 初始化数据库（修复权限、清理临时文件）
    db_initialized = DatabaseHelper.initialize_database(
        db_path=settings.vector_db_path,
        cleanup_temp=True
    )
    
    # 显示数据库健康状态
    health = DatabaseHelper.check_database_health(settings.vector_db_path)
    ...
```

### 3. 持久化配置

ChromaDB 配置正确使用持久化存储：

```python
# 在 vector_store.py 中
self.client = chromadb.PersistentClient(
    path=self.persist_directory,  # 持久化到 data/chroma
    settings=ChromaSettings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

## 使用方法

### 自动修复（推荐）

只需启动服务器，自动修复会在启动时执行：

```bash
# 使用虚拟环境的 Python
.venv/bin/python run_web.py

# 或
python run_web.py
```

启动时会看到类似输出：
```
🔧 正在初始化数据库...
  ✓ 数据库目录已创建: /path/to/data/chroma
  ✓ 数据库目录权限已设置: 755
  ✓ 已清理 3 个临时文件
  ✓ 数据库权限修复完成 (修复了 12 个项目)
  ✅ 数据库初始化完成

📊 数据库状态: 存在=True, 可读=True, 可写=True
📦 数据库大小: 0.5 MB, 文件数: 8
```

### 手动修复

如果遇到权限问题，也可以使用现有的脚本手动修复：

```bash
# 方案1：快速修复
bash quick_fix.sh

# 方案2：完整修复
bash fix_database_permissions.sh

# 方案3：完全重置（会删除所有数据）
bash reset_database.sh
```

## 数据持久化验证

### 测试步骤

1. **启动服务器**
   ```bash
   .venv/bin/python run_web.py
   ```

2. **上传测试数据**
   - 打开 http://localhost:8000
   - 切换到"知识库管理"
   - 上传一些文本到知识库
   - 记录上传的内容和知识库名称

3. **重启服务器**
   ```bash
   # 停止服务器（Ctrl+C 或）
   pkill -f run_web.py
   
   # 等待2秒
   sleep 2
   
   # 重新启动
   .venv/bin/python run_web.py
   ```

4. **验证数据是否保留**
   - 刷新浏览器页面
   - 切换到"知识库管理"
   - 点击"加载文档列表"
   - 确认之前上传的文档还在

5. **查询测试**
   - 切换到"RAG 问答"
   - 输入相关问题
   - 确认能检索到之前上传的内容

## 技术细节

### 文件权限说明

| 类型 | 权限 | 数值 | 说明 |
|------|------|------|------|
| 目录 | `rwxr-xr-x` | 755 | 所有者可读写执行，其他用户可读执行 |
| 文件 | `rw-r--r--` | 644 | 所有者可读写，其他用户只读 |

### ChromaDB 文件结构

```
data/chroma/
├── chroma.sqlite3           # 主数据库文件
├── [collection-id]/         # 每个集合一个目录
│   ├── data_level0.bin      # 向量数据
│   ├── header.bin           # 头信息
│   ├── length.bin           # 长度信息
│   └── link_lists.bin       # 链接列表
└── [其他临时文件]
```

### 清理的临时文件

- `*.tmp`: 临时文件
- `*-shm`: SQLite 共享内存文件
- `*-wal`: SQLite Write-Ahead Log 文件

这些文件在数据库正常关闭时应该被删除，但异常退出时可能残留，导致权限或锁定问题。

## 故障排除

### 问题1：重启后仍出现只读错误

**解决方案：**
```bash
# 1. 停止服务器
pkill -f run_web.py

# 2. 手动运行快速修复
bash quick_fix.sh

# 3. 检查权限
ls -la data/chroma

# 4. 重新启动
.venv/bin/python run_web.py
```

### 问题2：数据无法持久化

**检查清单：**
1. 确认数据库路径配置正确：
   ```python
   # 在 config.py 中
   vector_db_path: str = Field(
       default=str(PROJECT_ROOT / "data" / "chroma"),
       ...
   )
   ```

2. 确认使用 `PersistentClient` 而不是临时客户端

3. 检查磁盘空间：
   ```bash
   df -h .
   ```

### 问题3：旧数据查询不到

**可能原因：**
1. 集合名称不匹配（被规范化了）
   - 解决：使用"名称映射表"查看实际集合名称

2. 数据确实丢失
   - 检查：`data/chroma` 目录是否有文件
   - 恢复：如果有备份，从备份恢复

### 问题4：Permission Denied 错误

**解决方案：**
```bash
# 确保当前用户有权限
sudo chown -R $USER:$USER data/chroma

# 修复权限
bash fix_database_permissions.sh
```

## 预防措施

1. **定期备份**
   ```bash
   # 备份数据库目录
   tar -czf chroma_backup_$(date +%Y%m%d).tar.gz data/chroma/
   ```

2. **正确关闭服务器**
   - 使用 Ctrl+C 或 `pkill -f run_web.py`
   - 不要使用 `kill -9`（强制终止）

3. **监控磁盘空间**
   - 确保至少有 1GB 可用空间

4. **使用虚拟环境**
   - 确保依赖包版本一致
   - 避免权限问题

## 代码变更

### 新增文件
- `src/shuyixiao_agent/database_helper.py`: 数据库辅助工具类

### 修改文件
- `src/shuyixiao_agent/web_app.py`: 
  - 导入 `DatabaseHelper`
  - 在 `startup_event` 中调用数据库初始化
  - 显示数据库健康状态

## 验证清单

- [ ] 服务器启动时能看到数据库初始化信息
- [ ] 上传文档成功
- [ ] 重启服务器后数据仍然存在
- [ ] 文档列表能显示之前的文档
- [ ] RAG 问答能检索到历史数据
- [ ] 没有权限错误
- [ ] "名称映射表"显示正确

## 已知限制

1. **映射关系不持久化**: 
   - 知识库名称映射关系存储在内存中
   - 重启后需要重新建立（但数据不会丢失）
   
2. **多进程问题**:
   - 不建议同时运行多个服务器实例
   - ChromaDB 不支持多进程写入

3. **大数据集**:
   - 大量文档可能导致启动变慢
   - 建议单个集合不超过 100,000 个文档

## 更新日志

- 2024-10-13: 
  - 新增 `database_helper.py` 自动权限修复
  - 集成启动时数据库初始化
  - 添加数据库健康检查
  - 自动清理临时文件

## 相关文档

- [快速修复指南](quick_fix.sh)
- [数据库权限修复](fix_database_permissions.sh)
- [数据库重置](reset_database.sh)
- [名称映射显示](KNOWLEDGE_BASE_MAPPING_DISPLAY.md)
- [知识库同步修复](KNOWLEDGE_BASE_SYNC_FIX.md)

