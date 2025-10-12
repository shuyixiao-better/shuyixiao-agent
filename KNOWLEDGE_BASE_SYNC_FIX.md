# 知识库名称同步修复说明

## 问题描述

之前在 Web 界面中，上传文档到知识库后，无法在文档浏览器中查询到上传的文档。

### 问题根源

1. **多个独立的输入框**：页面上有多个知识库名称输入框（上传文本、上传文件、查看信息、文档浏览器等），它们之间没有同步
2. **名称规范化**：后端会将用户输入的知识库名称（如"舒一笑不秀头个人信息"）规范化为符合 ChromaDB 要求的格式（如"kb_dd65ff91_kb"）
3. **查询不一致**：用户在"上传文本"区域输入了知识库名称，但在"文档浏览器"区域仍然使用默认的"default"，导致查询不到数据

## 修复方案

### 1. 后端修改

修改了三个上传接口 (`/api/rag/upload/file`、`/api/rag/upload/directory`、`/api/rag/upload/texts`)，让它们返回规范化后的集合名称：

```python
return {
    "message": "文本上传成功",
    "collection_name": normalized_name,  # 返回规范化后的名称
    "original_name": request.collection_name,  # 保留原始名称
    "chunks_added": count,
    "total_documents": agent.get_document_count()
}
```

### 2. 前端修改

#### 添加同步函数

新增 `syncCollectionName()` 函数，用于同步所有知识库相关的输入框：

```javascript
function syncCollectionName(collectionName) {
    // 更新所有知识库相关的输入框
    document.getElementById('uploadCollection').value = collectionName;
    document.getElementById('fileUploadCollection').value = collectionName;
    document.getElementById('infoCollection').value = collectionName;
    document.getElementById('manageCollection').value = collectionName;
    document.getElementById('browserCollection').value = collectionName;
    document.getElementById('ragCollection').value = collectionName;
    
    console.log(`已同步知识库名称: ${collectionName}`);
}
```

#### 上传成功后自动同步

在文本和文件上传成功后，自动调用同步函数：

```javascript
if (response.ok) {
    const actualCollectionName = data.collection_name || collection;
    resultDiv.innerHTML = `<div class="alert alert-success">✓ 成功上传 ${data.chunks_added} 个文档片段到知识库 <strong>${actualCollectionName}</strong><br>总文档数: ${data.total_documents}</div>`;
    // 同步所有知识库名称输入框（使用实际的集合名称）
    syncCollectionName(actualCollectionName);
}
```

## 使用效果

1. **自动同步**：上传文档后，所有相关输入框会自动更新为实际使用的知识库名称
2. **显示实际名称**：上传成功提示会显示规范化后的实际集合名称，用户可以清楚地知道数据存储在哪个集合
3. **一致性保证**：避免了用户在不同区域使用不同知识库名称导致的查询失败

## 测试步骤

1. 启动 Web 服务器：`python run_web.py`
2. 打开浏览器访问 `http://localhost:8000`
3. 切换到"知识库管理"标签页
4. 在"上传文本"区域输入一个中文知识库名称（如"测试知识库"）
5. 输入一些文本内容，点击"上传文本"
6. 观察所有输入框是否自动更新为规范化后的名称（如"kb_12345678"）
7. 在"文档浏览器"区域点击"加载文档列表"
8. 确认可以看到刚才上传的文档

## 文件变更

- `src/shuyixiao_agent/web_app.py`：修改了上传接口，返回规范化后的集合名称
- `src/shuyixiao_agent/static/index.html`：添加了同步函数，上传成功后自动同步所有输入框

## 注意事项

- 知识库名称必须符合 ChromaDB 的要求：3-512 个字符，只包含 `[a-zA-Z0-9._-]`，必须以 `[a-zA-Z0-9]` 开头和结尾
- 中文或特殊字符会被自动转换为符合要求的格式
- 转换过程使用哈希值确保唯一性，同时保留部分可读性

