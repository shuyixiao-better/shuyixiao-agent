# 📦 安装指南

## 快速安装

### macOS / Linux

```bash
# 1. 进入项目目录
cd code_merge_assistant

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 测试安装
python3 test_example.py

# 4. 启动 Web 界面
python3 web_ui.py
```

### Windows

```cmd
# 1. 进入项目目录
cd code_merge_assistant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 测试安装
python test_example.py

# 4. 启动 Web 界面
python web_ui.py
```

## 依赖说明

本工具依赖以下 Python 包：

- `flask` - Web 界面框架
- `colorama` - 终端彩色输出（Windows 支持）
- `pyyaml` - YAML 配置文件解析
- `javalang` - Java 代码解析（可选）

所有依赖都是轻量级的，总大小 < 10 MB。

## 常见问题

### Q: pip 安装失败怎么办？

**方案 1：使用国内镜像**
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方案 2：使用 pip3**
```bash
pip3 install -r requirements.txt
```

**方案 3：逐个安装**
```bash
pip3 install flask
pip3 install colorama
pip3 install pyyaml
pip3 install javalang
```

### Q: Python 版本要求？

- 推荐：Python 3.7+
- 最低：Python 3.6

检查版本：
```bash
python3 --version
```

### Q: 没有 Python 怎么办？

**macOS:**
```bash
# 使用 Homebrew 安装
brew install python3
```

**Windows:**
1. 访问 https://www.python.org/downloads/
2. 下载并安装 Python 3.x
3. 安装时勾选 "Add Python to PATH"

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

## 验证安装

运行测试脚本：
```bash
python3 test_example.py
```

如果看到彩色的差异对比输出，说明安装成功！

## 下一步

安装完成后，查看 [快速开始.md](快速开始.md) 了解如何使用。
