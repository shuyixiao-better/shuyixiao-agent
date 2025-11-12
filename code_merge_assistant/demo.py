#!/usr/bin/env python3
"""快速演示脚本 - 无需安装依赖即可体验基础功能"""

import difflib
import sys


def simple_demo():
    """简单演示 - 不依赖任何第三方库"""
    
    print("=" * 80)
    print("🔀 代码合并辅助工具 - 快速演示")
    print("=" * 80)
    print()
    
    # 示例代码
    base_code = """public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}"""
    
    incoming_code = """public class Calculator {
    public int add(int a, int b) {
        // 添加参数校验
        if (a < 0 || b < 0) {
            throw new IllegalArgumentException("参数不能为负数");
        }
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}"""
    
    print("📄 基准版本（你的代码）：")
    print("-" * 80)
    print(base_code)
    print()
    
    print("📄 新版本（同事的代码）：")
    print("-" * 80)
    print(incoming_code)
    print()
    
    # 执行差异对比
    print("🔍 差异分析结果：")
    print("=" * 80)
    
    base_lines = base_code.splitlines(keepends=True)
    incoming_lines = incoming_code.splitlines(keepends=True)
    
    # 使用 difflib 进行对比
    differ = difflib.Differ()
    diff = list(differ.compare(base_lines, incoming_lines))
    
    added = 0
    deleted = 0
    modified = 0
    
    for line in diff:
        if line.startswith('+ '):
            added += 1
            print(f"[新增] {line[2:].rstrip()}")
        elif line.startswith('- '):
            deleted += 1
            print(f"[删除] {line[2:].rstrip()}")
        elif line.startswith('? '):
            continue
    
    print()
    print("=" * 80)
    print("📊 变更统计：")
    print(f"  • 新增：{added} 行")
    print(f"  • 删除：{deleted} 行")
    print("=" * 80)
    print()
    
    print("💡 提示：")
    print("  1. 安装完整依赖后，可以看到彩色高亮的差异")
    print("  2. 运行 'pip3 install -r requirements.txt' 安装依赖")
    print("  3. 运行 'python3 web_ui.py' 启动 Web 界面")
    print("  4. 运行 'python3 test_example.py' 查看完整功能演示")
    print()


def interactive_demo():
    """交互式演示"""
    print("=" * 80)
    print("🔀 交互式代码对比")
    print("=" * 80)
    print()
    print("请输入两段代码进行对比")
    print()
    
    print("【基准版本】")
    print("请输入代码（输入 'END' 结束）：")
    base_lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            base_lines.append(line)
        except EOFError:
            break
    
    print()
    print("【新版本】")
    print("请输入代码（输入 'END' 结束）：")
    incoming_lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            incoming_lines.append(line)
        except EOFError:
            break
    
    base_code = '\n'.join(base_lines)
    incoming_code = '\n'.join(incoming_lines)
    
    # 执行对比
    print()
    print("🔍 差异分析结果：")
    print("=" * 80)
    
    diff = difflib.unified_diff(
        base_code.splitlines(keepends=True),
        incoming_code.splitlines(keepends=True),
        fromfile='基准版本',
        tofile='新版本',
        lineterm=''
    )
    
    for line in diff:
        print(line)
    
    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_demo()
    else:
        simple_demo()
