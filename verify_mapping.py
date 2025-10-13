#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证旧知识库映射配置

快速检查配置是否生效
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def main():
    print("=" * 60)
    print("验证旧知识库映射配置")
    print("=" * 60)
    
    # 1. 读取配置文件
    print("\n1. 检查配置文件...")
    try:
        with open('knowledge_base_mappings.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            mappings = config.get('mappings', {})
            print(f"   ✓ 配置文件存在")
            print(f"   ✓ 找到 {len(mappings)} 个映射:")
            for encoded, original in mappings.items():
                print(f"      - '{encoded}' → '{original}'")
    except FileNotFoundError:
        print("   ✗ 配置文件不存在: knowledge_base_mappings.json")
        print("   请先创建配置文件")
        return
    except json.JSONDecodeError as e:
        print(f"   ✗ JSON格式错误: {e}")
        return
    
    # 2. 调用API验证
    print("\n2. 调用API验证映射...")
    try:
        response = requests.get(f"{BASE_URL}/api/rag/collections", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ API返回成功")
            print(f"   ✓ 找到 {data['total_count']} 个知识库:\n")
            
            # 检查每个配置的映射是否生效
            for encoded_name, expected_original in mappings.items():
                found = False
                for coll in data['collections']:
                    if coll['collection_name'] == encoded_name:
                        found = True
                        actual_original = coll.get('original_name') or coll['collection_name']
                        
                        print(f"   📚 {encoded_name}")
                        print(f"      期望原始名称: {expected_original}")
                        print(f"      实际原始名称: {actual_original}")
                        
                        if actual_original == expected_original:
                            print(f"      ✅ 映射成功！")
                        else:
                            print(f"      ⚠️  映射不匹配（可能需要重启服务器）")
                        print()
                        break
                
                if not found:
                    print(f"   ⚠️  知识库 {encoded_name} 不存在")
                    print()
        else:
            print(f"   ✗ API调用失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务器")
        print("   请确保服务器正在运行: python run_web.py")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)
    print("\n如果映射不匹配，请:")
    print("1. 检查配置文件格式是否正确")
    print("2. 重启服务器使配置生效")
    print("3. 刷新浏览器页面")

if __name__ == "__main__":
    main()

