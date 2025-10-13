#!/usr/bin/env python3
"""测试服务器响应"""
import requests
import sys

try:
    # 测试首页
    print("测试 GET /")
    response = requests.get("http://localhost:8000/")
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"响应长度: {len(response.text)} 字符")
    print(f"前100个字符: {response.text[:100]}")
    print()
    
    # 测试健康检查
    print("测试 GET /api/health")
    response = requests.get("http://localhost:8000/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)

