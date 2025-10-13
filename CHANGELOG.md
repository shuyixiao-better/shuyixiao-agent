# 更新日志

本文档记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- 会话记忆功能
- 多模态支持（图像、语音）
- 性能监控和日志
- 用户认证功能

## [0.3.0] - 2025-10-13

### 重大更新 - 项目整理与优化

#### 📝 文档优化
- ✨ 全新的 README.md，结构更清晰，内容更完整
- 📚 创建文档中心 (docs/README.md)，提供完整文档导航
- 🚀 新增 QUICKSTART.md 快速开始指南
- 🗑️ 删除30+个重复和过时的修复文档
- 📖 保留核心文档，移除冗余内容

#### 🧹 代码清理
- 🗑️ 删除20+个临时测试和诊断脚本
- 🗑️ 删除重复的配置示例文件
- 🗑️ 删除过时的工具脚本（fix_database_permissions.sh等）
- ✅ 保留核心功能代码和必要工具

#### ⚙️ 配置优化
- 📝 更新 env.example，添加完整的 RAG 配置说明
- 📝 添加模型分配配置说明
- 📝 统一配置文件，只保留 env.example

#### 🎯 项目结构
- 清理前：80+ 文件（大量重复文档和脚本）
- 清理后：精简到核心文件，结构更清晰
- 文档：从50个降到10个核心文档
- 脚本：只保留必要的启动脚本

### 删除的文件清单
**重复文档（34个）：**
- 🚀请先阅读我.md, START_HERE.md, QUICK_START.md 等快速开始文档
- SSL_FIX_*.md, 云端API优化说明.md 等修复文档
- DATABASE_*.md, KNOWLEDGE_BASE_*.md 等功能修复文档
- *_SUMMARY.md, *_FIX.md 等总结文档

**测试脚本（15个）：**
- test_*.py 系列测试脚本
- diagnose_*.py 诊断脚本
- verify_*.sh, *_fix.sh 验证和修复脚本
- migrate_*.py, show_*.py 迁移和展示脚本

**配置文件（3个）：**
- env_example.txt, env_config_example.txt
- knowledge_base_mappings.json

**启动脚本（2个）：**
- run_web_fixed.py, run_web_optimized.py

**文档（2个）：**
- docs/PROJECT_OVERVIEW.md, docs/pycharm_setup.md

### 保留的核心文件
**文档（10个）：**
- README.md - 主文档（全新）
- QUICKSTART.md - 快速开始（新增）
- CHANGELOG.md - 更新日志
- CONTRIBUTING.md - 贡献指南
- LICENSE - 许可证
- docs/*.md - 核心技术文档（10个）

**启动脚本（2个）：**
- run_web.py - 标准启动
- run_web_auto.py - 自动启动

**配置（1个）：**
- env.example - 配置示例

**代码：**
- src/ - 核心代码
- examples/ - 示例代码
- tests/ - 测试代码

### 影响
- ✅ 项目结构更清晰
- ✅ 文档更易查找和使用
- ✅ 减少维护负担
- ✅ 新用户更容易上手
- ✅ 代码库更精简

## [0.2.0] - 2025-10-10

### 新增
- ✨ **扩展工具集**：新增10个实用工具，总计13个内置工具
  - `get_random_number` - 生成随机数
  - `convert_temperature` - 温度单位转换
  - `string_reverse` - 字符串反转
  - `count_words` - 文本统计
  - `get_date_info` - 日期详细信息
  - `calculate_age` - 年龄计算
  - `generate_uuid` - UUID生成
  - `encode_base64` - Base64编码
  - `decode_base64` - Base64解码
  - `check_prime` - 质数检查
- 📚 新增完整的工具参考文档 (`docs/tools_reference.md`)
- 💡 新增完整工具集演示示例 (`examples/05_all_tools_demo.py`)
- 🔧 新增批量工具注册功能 (`get_basic_tools()`)

### 改进
- 📝 更新 README 文档，添加工具列表和使用示例
- 📖 更新示例文档，添加第5个示例说明
- 🎨 优化工具调用示例，展示批量注册方法

### 文档
- 📖 新增工具参考文档，详细说明所有13个工具的使用方法
- 📝 更新主README，添加工具表格和使用示例
- 📝 更新examples/README.md，添加新示例说明

## [0.1.0] - 2024-01-01

### 新增
- 🎉 初始版本发布
- ✨ 基于 LangGraph 的 Agent 框架
- 🤖 SimpleAgent - 简单对话 Agent
- 🛠️ ToolAgent - 支持工具调用的 Agent
- 📡 GiteeAIClient - 码云 AI API 客户端
- ⚙️ 基于 Pydantic 的配置管理
- 🔧 基础工具集（时间、计算、搜索）
- 📚 完整的文档和示例
- 💡 4 个示例程序
- ⚡ 故障转移支持

### 文档
- 📖 快速开始指南
- 📖 API 参考文档
- 📖 LangGraph 架构详解
- 📖 最佳实践指南
- 📖 示例代码说明

### 示例
- 示例 1：简单对话
- 示例 2：带工具的 Agent
- 示例 3：自定义工具
- 示例 4：直接使用 API 客户端

---

[未发布]: https://github.com/your-username/shuyixiao-agent/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/your-username/shuyixiao-agent/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-username/shuyixiao-agent/releases/tag/v0.1.0

