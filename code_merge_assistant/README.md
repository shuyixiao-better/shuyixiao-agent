# 🔀 代码合并辅助工具 (Code Merge Assistant)

## 📋 项目简介

一个专为**金融合规环境**设计的本地代码差异对比与合并辅助工具。

### 核心特性

- ✅ **智能差异分析**：基于 AST 语法树，理解代码结构而非简单文本对比
- 🎨 **可视化展示**：彩色高亮显示新增、删除、修改的代码块
- 📊 **统计摘要**：自动生成变更统计（新增/删除/修改的函数、类、方法等）
- 🔒 **完全本地**：无需联网，所有处理在本地完成，符合合规要求
- 🖥️ **跨平台**：支持 macOS 和 Windows
- 📝 **多语言支持**：支持 Java, Python, JavaScript, TypeScript 等主流语言

## 🚀 快速开始

### 安装依赖

```bash
cd code_merge_assistant
pip install -r requirements.txt
```

### 基础使用

```bash
# 对比两个文件
python merge_assistant.py compare file1.java file2.java

# 对比两段代码（从剪贴板或文本）
python merge_assistant.py compare-text

# 启动 Web 界面（推荐）
python web_ui.py
```

### Web 界面使用

1. 启动服务：`python web_ui.py`
2. 浏览器访问：`http://localhost:5678`
3. 粘贴两段代码，点击"对比分析"
4. 查看智能差异分析结果

## 📁 项目结构

```
code_merge_assistant/
├── README.md                 # 项目说明
├── requirements.txt          # Python 依赖
├── merge_assistant.py        # 命令行工具主程序
├── web_ui.py                # Web 界面服务
├── core/                    # 核心功能模块
│   ├── __init__.py
│   ├── diff_engine.py       # 差异分析引擎
│   ├── ast_parser.py        # AST 语法树解析
│   ├── merge_strategy.py    # 合并策略
│   └── formatter.py         # 输出格式化
├── templates/               # Web 界面模板
│   └── index.html
└── config/                  # 配置文件
    └── rules.yaml           # 合并规则配置
```

## 🎯 使用场景

1. **企业微信代码传输**：同事通过企业微信发送代码片段，快速对比差异
2. **跨环境代码同步**：对比内外网环境的代码版本差异
3. **代码审查**：快速识别代码变更的关键部分
4. **合并决策辅助**：智能建议保留哪些变更

## 🔧 配置说明

编辑 `config/rules.yaml` 自定义合并规则：

```yaml
# 优先级规则
priority:
  - type: "import"
    strategy: "keep_both"  # 保留双方的 import
  - type: "config"
    strategy: "prefer_base"  # 配置项优先保留基准版本
  - type: "business_logic"
    strategy: "prefer_incoming"  # 业务逻辑优先保留新版本

# 忽略规则
ignore:
  - "comments"  # 忽略注释差异
  - "whitespace"  # 忽略空格差异
```

## 📊 输出示例

```
📊 代码差异分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 变更统计：
  • 新增方法：3 个
  • 修改方法：2 个
  • 删除方法：1 个
  • 配置变更：5 处

🔍 详细差异：

[类] UserService
  ✅ 新增方法：getUserById(Long id)
  ⚠️  修改方法：updateUser(User user)
    - 第 45 行：添加了参数校验
    - 第 52 行：修改了返回值类型
  ❌ 删除方法：deprecatedMethod()

[配置] application.properties
  ⚠️  修改：database.url
    基准版本：jdbc:mysql://localhost:3306/db
    新版本：  jdbc:mysql://prod-server:3306/db
    💡 建议：保留基准版本（生产环境配置）
```

## 🛡️ 安全与合规

- ✅ 完全本地运行，无外网连接
- ✅ 不存储任何代码到磁盘（可选内存模式）
- ✅ 支持操作日志记录，满足审计要求
- ✅ 可配置敏感信息脱敏规则

## 📝 开发计划

- [x] 基础差异对比功能
- [x] Web 界面
- [x] Java 语言支持
- [ ] Python/JavaScript 语言支持
- [ ] 三方合并支持
- [ ] 历史记录管理
- [ ] 导出合并报告

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
