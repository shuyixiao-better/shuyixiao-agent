"""
测试新增的10个工具

用于验证所有新增工具的功能是否正常
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 直接导入工具模块
from src.shuyixiao_agent.tools.basic_tools import (
    get_random_number,
    convert_temperature,
    string_reverse,
    count_words,
    get_date_info,
    calculate_age,
    generate_uuid,
    encode_base64,
    decode_base64,
    check_prime
)


def test_get_random_number():
    """测试随机数生成"""
    print("测试 get_random_number...")
    
    # 测试默认范围
    num = get_random_number()
    assert 1 <= num <= 100, "随机数应在1-100之间"
    print(f"  ✓ 生成随机数: {num}")
    
    # 测试自定义范围
    num = get_random_number(1, 10)
    assert 1 <= num <= 10, "随机数应在1-10之间"
    print(f"  ✓ 生成随机数(1-10): {num}")


def test_convert_temperature():
    """测试温度转换"""
    print("测试 convert_temperature...")
    
    # 摄氏度转华氏度
    result = convert_temperature(0, "C", "F")
    assert result == 32.0, f"0°C应该等于32°F，但得到{result}"
    print(f"  ✓ 0°C = {result}°F")
    
    # 华氏度转摄氏度
    result = convert_temperature(32, "F", "C")
    assert result == 0.0, f"32°F应该等于0°C，但得到{result}"
    print(f"  ✓ 32°F = {result}°C")
    
    # 摄氏度转开尔文
    result = convert_temperature(0, "C", "K")
    assert result == 273.15, f"0°C应该等于273.15K，但得到{result}"
    print(f"  ✓ 0°C = {result}K")


def test_string_reverse():
    """测试字符串反转"""
    print("测试 string_reverse...")
    
    result = string_reverse("Hello")
    assert result == "olleH", f"'Hello'反转应为'olleH'，但得到'{result}'"
    print(f"  ✓ 'Hello' -> '{result}'")
    
    result = string_reverse("12345")
    assert result == "54321", f"'12345'反转应为'54321'，但得到'{result}'"
    print(f"  ✓ '12345' -> '{result}'")


def test_count_words():
    """测试文本统计"""
    print("测试 count_words...")
    
    text = "Hello World"
    result = count_words(text)
    assert result["total_words"] == 2, "应该有2个单词"
    assert result["total_characters"] == 11, "应该有11个字符"
    print(f"  ✓ 'Hello World' -> {result['total_words']}个单词, {result['total_characters']}个字符")


def test_get_date_info():
    """测试日期信息"""
    print("测试 get_date_info...")
    
    # 测试指定日期
    result = get_date_info("2025-10-10")
    assert result["date"] == "2025-10-10"
    assert "weekday" in result
    assert "day_of_year" in result
    print(f"  ✓ 2025-10-10: {result['weekday']}, 第{result['day_of_year']}天")
    
    # 测试当前日期
    result = get_date_info()
    assert "date" in result
    print(f"  ✓ 今天: {result['date']}, {result['weekday']}")


def test_calculate_age():
    """测试年龄计算"""
    print("测试 calculate_age...")
    
    # 注意：这个测试结果会随时间变化
    result = calculate_age("2000-01-01")
    assert "age_years" in result
    assert "total_days" in result
    assert result["birth_date"] == "2000-01-01"
    print(f"  ✓ 2000-01-01出生: {result['age_years']}岁, {result['total_days']}天")


def test_generate_uuid():
    """测试UUID生成"""
    print("测试 generate_uuid...")
    
    # 测试UUID v4
    uuid = generate_uuid()
    assert len(uuid) == 36, "UUID应该是36个字符"
    assert uuid.count("-") == 4, "UUID应该有4个连字符"
    print(f"  ✓ UUID v4: {uuid}")
    
    # 测试UUID v1
    uuid = generate_uuid(version=1)
    assert len(uuid) == 36, "UUID应该是36个字符"
    print(f"  ✓ UUID v1: {uuid}")


def test_encode_decode_base64():
    """测试Base64编码解码"""
    print("测试 encode_base64 和 decode_base64...")
    
    text = "Hello World"
    
    # 编码
    encoded = encode_base64(text)
    assert encoded == "SGVsbG8gV29ybGQ=", f"编码结果不正确: {encoded}"
    print(f"  ✓ 编码: '{text}' -> '{encoded}'")
    
    # 解码
    decoded = decode_base64(encoded)
    assert decoded == text, f"解码结果不正确: {decoded}"
    print(f"  ✓ 解码: '{encoded}' -> '{decoded}'")


def test_check_prime():
    """测试质数检查"""
    print("测试 check_prime...")
    
    # 测试质数
    result = check_prime(17)
    assert result["is_prime"] == True, "17应该是质数"
    print(f"  ✓ 17: 是质数")
    
    # 测试非质数
    result = check_prime(18)
    assert result["is_prime"] == False, "18不应该是质数"
    print(f"  ✓ 18: 不是质数 ({result['reason']})")
    
    # 测试特殊情况
    result = check_prime(2)
    assert result["is_prime"] == True, "2应该是质数"
    print(f"  ✓ 2: 是质数")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试新增的10个工具")
    print("=" * 60)
    print()
    
    tests = [
        test_get_random_number,
        test_convert_temperature,
        test_string_reverse,
        test_count_words,
        test_get_date_info,
        test_calculate_age,
        test_generate_uuid,
        test_encode_decode_base64,
        test_check_prime
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            failed += 1
            print(f"  ✗ 测试失败: {str(e)}")
            print()
    
    print("=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

