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

