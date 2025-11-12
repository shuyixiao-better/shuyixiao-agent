#!/usr/bin/env python3
"""测试示例 - 演示工具的使用"""

from core.diff_engine import DiffEngine
from core.formatter import ConsoleFormatter
from core.ast_parser import SimpleASTParser
from core.merge_strategy import MergeStrategy


def test_basic_diff():
    """测试基础差异对比"""
    print("=" * 80)
    print("测试 1: 基础差异对比")
    print("=" * 80)
    
    base_code = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
"""
    
    incoming_code = """
public class Calculator {
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
}
"""
    
    engine = DiffEngine()
    result = engine.analyze(base_code, incoming_code)
    
    formatter = ConsoleFormatter()
    output = formatter.format_diff(result)
    print(output)


def test_java_file():
    """测试 Java 文件对比"""
    print("\n" + "=" * 80)
    print("测试 2: Java 文件对比")
    print("=" * 80)
    
    try:
        with open('examples/example1_base.java', 'r', encoding='utf-8') as f:
            base_code = f.read()
        
        with open('examples/example1_incoming.java', 'r', encoding='utf-8') as f:
            incoming_code = f.read()
        
        engine = DiffEngine()
        result = engine.analyze(base_code, incoming_code)
        
        formatter = ConsoleFormatter()
        output = formatter.format_diff(result)
        print(output)
        
    except FileNotFoundError:
        print("⚠️  示例文件不存在，跳过此测试")


def test_ast_analysis():
    """测试 AST 智能分析"""
    print("\n" + "=" * 80)
    print("测试 3: AST 智能分析")
    print("=" * 80)
    
    base_code = """
public class UserService {
    public User getUser(Long id) {
        return repository.findById(id);
    }
}
"""
    
    incoming_code = """
public class UserService {
    public User getUser(Long id) throws UserNotFoundException {
        return repository.findById(id)
            .orElseThrow(() -> new UserNotFoundException());
    }
    
    public void deleteUser(Long id) {
        repository.deleteById(id);
    }
}
"""
    
    strategy = MergeStrategy()
    result = strategy.analyze_with_context(base_code, incoming_code)
    
    print("\n📊 代码块分析：")
    print(f"\n基准版本包含 {len(result['base_blocks'])} 个代码块")
    print(f"新版本包含 {len(result['incoming_blocks'])} 个代码块")
    
    block_diff = result['block_diff']
    print(f"\n变更统计：")
    print(f"  • 新增：{len(block_diff['added'])} 个")
    print(f"  • 删除：{len(block_diff['deleted'])} 个")
    print(f"  • 修改：{len(block_diff['modified'])} 个")
    
    print("\n" + strategy.format_suggestions(result['suggestions']))


def test_side_by_side():
    """测试并排对比"""
    print("\n" + "=" * 80)
    print("测试 4: 并排对比视图")
    print("=" * 80)
    
    base_code = """line 1
line 2
line 3 old
line 4"""
    
    incoming_code = """line 1
line 2
line 3 new
line 4
line 5"""
    
    engine = DiffEngine()
    result = engine.analyze(base_code, incoming_code)
    
    formatter = ConsoleFormatter()
    output = formatter.format_side_by_side(base_code, incoming_code, result['changes'])
    print(output)


if __name__ == '__main__':
    print("\n🔀 代码合并辅助工具 - 功能测试\n")
    
    try:
        test_basic_diff()
        test_java_file()
        test_ast_analysis()
        test_side_by_side()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        print("\n💡 提示：运行 'python web_ui.py' 启动 Web 界面体验完整功能")
        
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
