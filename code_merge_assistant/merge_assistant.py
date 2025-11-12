#!/usr/bin/env python3
"""代码合并辅助工具 - 命令行入口"""

import sys
import argparse
from pathlib import Path
from core.diff_engine import DiffEngine
from core.formatter import ConsoleFormatter


def read_file(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        sys.exit(1)


def compare_files(base_file: str, incoming_file: str):
    """对比两个文件"""
    print(f"📂 正在对比文件...")
    print(f"   基准版本: {base_file}")
    print(f"   新版本: {incoming_file}")
    
    base_code = read_file(base_file)
    incoming_code = read_file(incoming_file)
    
    # 执行差异分析
    engine = DiffEngine()
    result = engine.analyze(base_code, incoming_code)
    
    # 格式化输出
    formatter = ConsoleFormatter()
    output = formatter.format_diff(result)
    print(output)
    
    # 询问是否需要并排对比
    try:
        choice = input("\n是否需要并排对比视图？(y/n): ").strip().lower()
        if choice == 'y':
            side_by_side = formatter.format_side_by_side(
                base_code, incoming_code, result["changes"]
            )
            print(side_by_side)
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
        sys.exit(0)


def compare_text():
    """对比两段文本（交互式输入）"""
    print("📝 请输入代码进行对比")
    print("=" * 60)
    
    print("\n【基准版本】")
    print("请粘贴你的代码，输入完成后按 Ctrl+D (Mac/Linux) 或 Ctrl+Z (Windows) 然后回车：")
    try:
        base_lines = []
        while True:
            try:
                line = input()
                base_lines.append(line)
            except EOFError:
                break
        base_code = '\n'.join(base_lines)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(0)
    
    print("\n【新版本】")
    print("请粘贴同事的代码，输入完成后按 Ctrl+D (Mac/Linux) 或 Ctrl+Z (Windows) 然后回车：")
    try:
        incoming_lines = []
        while True:
            try:
                line = input()
                incoming_lines.append(line)
            except EOFError:
                break
        incoming_code = '\n'.join(incoming_lines)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(0)
    
    # 执行差异分析
    engine = DiffEngine()
    result = engine.analyze(base_code, incoming_code)
    
    # 格式化输出
    formatter = ConsoleFormatter()
    output = formatter.format_diff(result)
    print(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🔀 代码合并辅助工具 - 智能代码差异对比",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 对比两个文件
  python merge_assistant.py compare file1.java file2.java
  
  # 交互式输入代码对比
  python merge_assistant.py compare-text
  
  # 启动 Web 界面
  python web_ui.py
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # compare 命令
    compare_parser = subparsers.add_parser('compare', help='对比两个文件')
    compare_parser.add_argument('base_file', help='基准文件（你的版本）')
    compare_parser.add_argument('incoming_file', help='新文件（同事的版本）')
    
    # compare-text 命令
    subparsers.add_parser('compare-text', help='交互式输入代码对比')
    
    args = parser.parse_args()
    
    if args.command == 'compare':
        compare_files(args.base_file, args.incoming_file)
    elif args.command == 'compare-text':
        compare_text()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
