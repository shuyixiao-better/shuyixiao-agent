"""
预定义工具集合 - Tool Use Agent 的内置工具

包含常用的工具类型：
- 文件操作工具
- 网络请求工具  
- 数据处理工具
- 系统信息工具
- 计算工具
- 文本处理工具
"""

import os
import json
import csv
import requests
import platform
import psutil
import math
import statistics
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import subprocess
import sys

from ..agents.tool_use_agent import ToolDefinition, ToolParameter, ToolType


class FileOperationTools:
    """文件操作工具集"""
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> str:
        """写入文件内容"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return f"文件写入成功: {file_path}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"
    
    @staticmethod
    def list_directory(directory_path: str, show_hidden: bool = False) -> str:
        """列出目录内容"""
        try:
            items = []
            for item in os.listdir(directory_path):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(directory_path, item)
                item_type = "目录" if os.path.isdir(item_path) else "文件"
                size = os.path.getsize(item_path) if os.path.isfile(item_path) else "-"
                items.append(f"{item_type}: {item} ({size} bytes)" if size != "-" else f"{item_type}: {item}")
            
            return f"目录 {directory_path} 内容:\n" + "\n".join(items)
        except Exception as e:
            return f"列出目录失败: {str(e)}"
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(file_path)
    
    @staticmethod
    def get_file_info(file_path: str) -> str:
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return "文件不存在"
            
            stat = os.stat(file_path)
            info = {
                "文件路径": file_path,
                "文件大小": f"{stat.st_size} bytes",
                "创建时间": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "是否为目录": os.path.isdir(file_path),
                "是否为文件": os.path.isfile(file_path)
            }
            
            return json.dumps(info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取文件信息失败: {str(e)}"
    
    @staticmethod
    def delete_file(file_path: str) -> str:
        """删除文件"""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return f"文件删除成功: {file_path}"
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                return f"目录删除成功: {file_path}"
            else:
                return "文件或目录不存在"
        except Exception as e:
            return f"删除失败: {str(e)}"


class NetworkTools:
    """网络请求工具集"""
    
    @staticmethod
    def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> str:
        """发送HTTP GET请求"""
        try:
            response = requests.get(url, headers=headers or {}, timeout=timeout)
            return json.dumps({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:1000],  # 限制内容长度
                "success": response.status_code == 200
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"HTTP GET请求失败: {str(e)}"
    
    @staticmethod
    def http_post(url: str, data: Optional[Dict[str, Any]] = None, 
                  json_data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> str:
        """发送HTTP POST请求"""
        try:
            response = requests.post(
                url, 
                data=data, 
                json=json_data,
                headers=headers or {}, 
                timeout=timeout
            )
            return json.dumps({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text[:1000],
                "success": response.status_code in [200, 201]
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"HTTP POST请求失败: {str(e)}"
    
    @staticmethod
    def ping_host(host: str, count: int = 4) -> str:
        """Ping主机"""
        try:
            if platform.system().lower() == "windows":
                cmd = f"ping -n {count} {host}"
            else:
                cmd = f"ping -c {count} {host}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return f"Ping结果:\n{result.stdout}"
        except Exception as e:
            return f"Ping失败: {str(e)}"


class DataProcessingTools:
    """数据处理工具集"""
    
    @staticmethod
    def parse_json(json_string: str) -> str:
        """解析JSON字符串"""
        try:
            data = json.loads(json_string)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"JSON解析失败: {str(e)}"
    
    @staticmethod
    def parse_csv(csv_content: str, delimiter: str = ',') -> str:
        """解析CSV内容"""
        try:
            import io
            reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
            data = list(reader)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"CSV解析失败: {str(e)}"
    
    @staticmethod
    def filter_data(data_json: str, filter_key: str, filter_value: str) -> str:
        """过滤数据"""
        try:
            data = json.loads(data_json)
            if isinstance(data, list):
                filtered = [item for item in data if str(item.get(filter_key, '')) == filter_value]
            else:
                filtered = data if str(data.get(filter_key, '')) == filter_value else {}
            
            return json.dumps(filtered, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"数据过滤失败: {str(e)}"
    
    @staticmethod
    def sort_data(data_json: str, sort_key: str, reverse: bool = False) -> str:
        """排序数据"""
        try:
            data = json.loads(data_json)
            if isinstance(data, list):
                sorted_data = sorted(data, key=lambda x: x.get(sort_key, ''), reverse=reverse)
            else:
                sorted_data = data
            
            return json.dumps(sorted_data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"数据排序失败: {str(e)}"
    
    @staticmethod
    def aggregate_data(data_json: str, group_key: str, agg_key: str, operation: str = 'sum') -> str:
        """聚合数据"""
        try:
            data = json.loads(data_json)
            if not isinstance(data, list):
                return "数据必须是数组格式"
            
            groups = {}
            for item in data:
                group_value = item.get(group_key, 'unknown')
                if group_value not in groups:
                    groups[group_value] = []
                
                agg_value = item.get(agg_key, 0)
                if isinstance(agg_value, (int, float)):
                    groups[group_value].append(agg_value)
            
            result = {}
            for group, values in groups.items():
                if operation == 'sum':
                    result[group] = sum(values)
                elif operation == 'avg':
                    result[group] = sum(values) / len(values) if values else 0
                elif operation == 'count':
                    result[group] = len(values)
                elif operation == 'max':
                    result[group] = max(values) if values else 0
                elif operation == 'min':
                    result[group] = min(values) if values else 0
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"数据聚合失败: {str(e)}"


class SystemInfoTools:
    """系统信息工具集"""
    
    @staticmethod
    def get_system_info() -> str:
        """获取系统信息"""
        try:
            info = {
                "操作系统": platform.system(),
                "系统版本": platform.release(),
                "架构": platform.machine(),
                "处理器": platform.processor(),
                "Python版本": sys.version,
                "主机名": platform.node()
            }
            return json.dumps(info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取系统信息失败: {str(e)}"
    
    @staticmethod
    def get_cpu_info() -> str:
        """获取CPU信息"""
        try:
            info = {
                "CPU核心数": psutil.cpu_count(logical=False),
                "逻辑CPU数": psutil.cpu_count(logical=True),
                "CPU使用率": f"{psutil.cpu_percent(interval=1):.2f}%",
                "CPU频率": f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "未知"
            }
            return json.dumps(info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取CPU信息失败: {str(e)}"
    
    @staticmethod
    def get_memory_info() -> str:
        """获取内存信息"""
        try:
            memory = psutil.virtual_memory()
            info = {
                "总内存": f"{memory.total / (1024**3):.2f} GB",
                "可用内存": f"{memory.available / (1024**3):.2f} GB",
                "已使用内存": f"{memory.used / (1024**3):.2f} GB",
                "内存使用率": f"{memory.percent:.2f}%"
            }
            return json.dumps(info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取内存信息失败: {str(e)}"
    
    @staticmethod
    def get_disk_info() -> str:
        """获取磁盘信息"""
        try:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "设备": partition.device,
                        "挂载点": partition.mountpoint,
                        "文件系统": partition.fstype,
                        "总空间": f"{usage.total / (1024**3):.2f} GB",
                        "已使用": f"{usage.used / (1024**3):.2f} GB",
                        "可用空间": f"{usage.free / (1024**3):.2f} GB",
                        "使用率": f"{(usage.used / usage.total * 100):.2f}%"
                    })
                except PermissionError:
                    continue
            
            return json.dumps(disk_info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取磁盘信息失败: {str(e)}"
    
    @staticmethod
    def get_process_list(limit: int = 10) -> str:
        """获取进程列表"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return json.dumps(processes[:limit], ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取进程列表失败: {str(e)}"


class CalculationTools:
    """计算工具集"""
    
    @staticmethod
    def basic_math(expression: str) -> str:
        """基础数学计算"""
        try:
            # 安全的数学表达式计算
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"计算失败: {str(e)}"
    
    @staticmethod
    def statistics_calc(numbers: List[float], operation: str = 'mean') -> str:
        """统计计算"""
        try:
            if not numbers:
                return "数字列表不能为空"
            
            if operation == 'mean':
                result = statistics.mean(numbers)
            elif operation == 'median':
                result = statistics.median(numbers)
            elif operation == 'mode':
                result = statistics.mode(numbers)
            elif operation == 'stdev':
                result = statistics.stdev(numbers) if len(numbers) > 1 else 0
            elif operation == 'variance':
                result = statistics.variance(numbers) if len(numbers) > 1 else 0
            elif operation == 'sum':
                result = sum(numbers)
            elif operation == 'max':
                result = max(numbers)
            elif operation == 'min':
                result = min(numbers)
            else:
                return f"不支持的操作: {operation}"
            
            return str(result)
        except Exception as e:
            return f"统计计算失败: {str(e)}"
    
    @staticmethod
    def unit_conversion(value: float, from_unit: str, to_unit: str, unit_type: str = 'length') -> str:
        """单位转换"""
        try:
            conversions = {
                'length': {
                    'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000,
                    'inch': 0.0254, 'ft': 0.3048, 'yard': 0.9144, 'mile': 1609.34
                },
                'weight': {
                    'mg': 0.000001, 'g': 0.001, 'kg': 1, 'ton': 1000,
                    'oz': 0.0283495, 'lb': 0.453592
                },
                'temperature': {
                    'celsius': lambda x: x,
                    'fahrenheit': lambda x: (x - 32) * 5/9,
                    'kelvin': lambda x: x - 273.15
                }
            }
            
            if unit_type == 'temperature':
                # 温度转换需要特殊处理
                if from_unit == 'celsius':
                    celsius_value = value
                elif from_unit == 'fahrenheit':
                    celsius_value = (value - 32) * 5/9
                elif from_unit == 'kelvin':
                    celsius_value = value - 273.15
                else:
                    return f"不支持的温度单位: {from_unit}"
                
                if to_unit == 'celsius':
                    result = celsius_value
                elif to_unit == 'fahrenheit':
                    result = celsius_value * 9/5 + 32
                elif to_unit == 'kelvin':
                    result = celsius_value + 273.15
                else:
                    return f"不支持的温度单位: {to_unit}"
            else:
                if unit_type not in conversions:
                    return f"不支持的单位类型: {unit_type}"
                
                unit_dict = conversions[unit_type]
                if from_unit not in unit_dict or to_unit not in unit_dict:
                    return f"不支持的单位: {from_unit} 或 {to_unit}"
                
                # 转换为基础单位，再转换为目标单位
                base_value = value * unit_dict[from_unit]
                result = base_value / unit_dict[to_unit]
            
            return f"{value} {from_unit} = {result} {to_unit}"
        except Exception as e:
            return f"单位转换失败: {str(e)}"


class TextProcessingTools:
    """文本处理工具集"""
    
    @staticmethod
    def text_analysis(text: str) -> str:
        """文本分析"""
        try:
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            paragraphs = text.split('\n\n')
            
            analysis = {
                "字符数": len(text),
                "单词数": len(words),
                "句子数": len([s for s in sentences if s.strip()]),
                "段落数": len([p for p in paragraphs if p.strip()]),
                "平均单词长度": sum(len(word) for word in words) / len(words) if words else 0,
                "最长单词": max(words, key=len) if words else "",
                "最短单词": min(words, key=len) if words else ""
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"文本分析失败: {str(e)}"
    
    @staticmethod
    def text_search_replace(text: str, search_pattern: str, replacement: str, use_regex: bool = False) -> str:
        """文本搜索替换"""
        try:
            if use_regex:
                result = re.sub(search_pattern, replacement, text)
            else:
                result = text.replace(search_pattern, replacement)
            
            return result
        except Exception as e:
            return f"文本替换失败: {str(e)}"
    
    @staticmethod
    def text_extract_pattern(text: str, pattern: str) -> str:
        """提取文本模式"""
        try:
            matches = re.findall(pattern, text)
            return json.dumps(matches, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"模式提取失败: {str(e)}"
    
    @staticmethod
    def text_hash(text: str, algorithm: str = 'md5') -> str:
        """计算文本哈希"""
        try:
            text_bytes = text.encode('utf-8')
            
            if algorithm == 'md5':
                hash_obj = hashlib.md5(text_bytes)
            elif algorithm == 'sha1':
                hash_obj = hashlib.sha1(text_bytes)
            elif algorithm == 'sha256':
                hash_obj = hashlib.sha256(text_bytes)
            else:
                return f"不支持的哈希算法: {algorithm}"
            
            return hash_obj.hexdigest()
        except Exception as e:
            return f"哈希计算失败: {str(e)}"
    
    @staticmethod
    def text_format(text: str, operation: str = 'upper') -> str:
        """文本格式化"""
        try:
            if operation == 'upper':
                return text.upper()
            elif operation == 'lower':
                return text.lower()
            elif operation == 'title':
                return text.title()
            elif operation == 'capitalize':
                return text.capitalize()
            elif operation == 'strip':
                return text.strip()
            elif operation == 'reverse':
                return text[::-1]
            else:
                return f"不支持的操作: {operation}"
        except Exception as e:
            return f"文本格式化失败: {str(e)}"


class PredefinedToolsRegistry:
    """预定义工具注册器"""
    
    @staticmethod
    def get_all_tools() -> List[ToolDefinition]:
        """获取所有预定义工具"""
        tools = []
        
        # 文件操作工具
        tools.extend([
            ToolDefinition(
                name="read_file",
                description="读取文件内容",
                function=FileOperationTools.read_file,
                parameters=[
                    ToolParameter("file_path", "string", "文件路径", True),
                    ToolParameter("encoding", "string", "文件编码", False, "utf-8")
                ],
                tool_type=ToolType.FILE_OPERATION,
                examples=["读取config.txt文件", "查看日志文件内容"],
                tags=["文件", "读取", "IO"]
            ),
            ToolDefinition(
                name="write_file",
                description="写入文件内容",
                function=FileOperationTools.write_file,
                parameters=[
                    ToolParameter("file_path", "string", "文件路径", True),
                    ToolParameter("content", "string", "文件内容", True),
                    ToolParameter("encoding", "string", "文件编码", False, "utf-8")
                ],
                tool_type=ToolType.FILE_OPERATION,
                examples=["保存配置到文件", "创建新的文本文件"],
                tags=["文件", "写入", "保存"]
            ),
            ToolDefinition(
                name="list_directory",
                description="列出目录内容",
                function=FileOperationTools.list_directory,
                parameters=[
                    ToolParameter("directory_path", "string", "目录路径", True),
                    ToolParameter("show_hidden", "boolean", "显示隐藏文件", False, False)
                ],
                tool_type=ToolType.FILE_OPERATION,
                examples=["查看当前目录文件", "列出项目文件夹内容"],
                tags=["目录", "文件列表"]
            ),
            ToolDefinition(
                name="get_file_info",
                description="获取文件详细信息",
                function=FileOperationTools.get_file_info,
                parameters=[
                    ToolParameter("file_path", "string", "文件路径", True)
                ],
                tool_type=ToolType.FILE_OPERATION,
                examples=["查看文件大小和修改时间", "检查文件属性"],
                tags=["文件", "信息", "属性"]
            )
        ])
        
        # 网络工具
        tools.extend([
            ToolDefinition(
                name="http_get",
                description="发送HTTP GET请求",
                function=NetworkTools.http_get,
                parameters=[
                    ToolParameter("url", "string", "请求URL", True),
                    ToolParameter("headers", "object", "请求头", False, None),
                    ToolParameter("timeout", "integer", "超时时间(秒)", False, 30)
                ],
                tool_type=ToolType.NETWORK_REQUEST,
                examples=["获取API数据", "检查网站状态"],
                tags=["HTTP", "GET", "网络"]
            ),
            ToolDefinition(
                name="http_post",
                description="发送HTTP POST请求",
                function=NetworkTools.http_post,
                parameters=[
                    ToolParameter("url", "string", "请求URL", True),
                    ToolParameter("data", "object", "表单数据", False, None),
                    ToolParameter("json_data", "object", "JSON数据", False, None),
                    ToolParameter("headers", "object", "请求头", False, None),
                    ToolParameter("timeout", "integer", "超时时间(秒)", False, 30)
                ],
                tool_type=ToolType.NETWORK_REQUEST,
                examples=["提交表单数据", "调用API接口"],
                tags=["HTTP", "POST", "网络"]
            ),
            ToolDefinition(
                name="ping_host",
                description="Ping网络主机",
                function=NetworkTools.ping_host,
                parameters=[
                    ToolParameter("host", "string", "主机地址", True),
                    ToolParameter("count", "integer", "ping次数", False, 4)
                ],
                tool_type=ToolType.NETWORK_REQUEST,
                examples=["检查网络连通性", "测试服务器响应"],
                tags=["ping", "网络", "连通性"]
            )
        ])
        
        # 数据处理工具
        tools.extend([
            ToolDefinition(
                name="parse_json",
                description="解析JSON字符串",
                function=DataProcessingTools.parse_json,
                parameters=[
                    ToolParameter("json_string", "string", "JSON字符串", True)
                ],
                tool_type=ToolType.DATA_PROCESSING,
                examples=["解析API返回的JSON", "格式化JSON数据"],
                tags=["JSON", "解析", "数据"]
            ),
            ToolDefinition(
                name="filter_data",
                description="过滤JSON数据",
                function=DataProcessingTools.filter_data,
                parameters=[
                    ToolParameter("data_json", "string", "JSON数据", True),
                    ToolParameter("filter_key", "string", "过滤字段", True),
                    ToolParameter("filter_value", "string", "过滤值", True)
                ],
                tool_type=ToolType.DATA_PROCESSING,
                examples=["筛选特定条件的数据", "过滤用户列表"],
                tags=["过滤", "数据", "筛选"]
            ),
            ToolDefinition(
                name="aggregate_data",
                description="聚合数据统计",
                function=DataProcessingTools.aggregate_data,
                parameters=[
                    ToolParameter("data_json", "string", "JSON数据", True),
                    ToolParameter("group_key", "string", "分组字段", True),
                    ToolParameter("agg_key", "string", "聚合字段", True),
                    ToolParameter("operation", "string", "聚合操作(sum/avg/count/max/min)", False, "sum")
                ],
                tool_type=ToolType.DATA_PROCESSING,
                examples=["按类别统计销售额", "计算平均分数"],
                tags=["聚合", "统计", "分组"]
            )
        ])
        
        # 系统信息工具
        tools.extend([
            ToolDefinition(
                name="get_system_info",
                description="获取系统基本信息",
                function=SystemInfoTools.get_system_info,
                parameters=[],
                tool_type=ToolType.SYSTEM_INFO,
                examples=["查看操作系统版本", "获取系统架构信息"],
                tags=["系统", "信息", "版本"]
            ),
            ToolDefinition(
                name="get_cpu_info",
                description="获取CPU信息",
                function=SystemInfoTools.get_cpu_info,
                parameters=[],
                tool_type=ToolType.SYSTEM_INFO,
                examples=["查看CPU使用率", "获取处理器信息"],
                tags=["CPU", "性能", "监控"]
            ),
            ToolDefinition(
                name="get_memory_info",
                description="获取内存信息",
                function=SystemInfoTools.get_memory_info,
                parameters=[],
                tool_type=ToolType.SYSTEM_INFO,
                examples=["检查内存使用情况", "查看可用内存"],
                tags=["内存", "RAM", "监控"]
            )
        ])
        
        # 计算工具
        tools.extend([
            ToolDefinition(
                name="basic_math",
                description="基础数学计算",
                function=CalculationTools.basic_math,
                parameters=[
                    ToolParameter("expression", "string", "数学表达式", True)
                ],
                tool_type=ToolType.CALCULATION,
                examples=["计算 2+3*4", "求解 sqrt(16)"],
                tags=["数学", "计算", "表达式"]
            ),
            ToolDefinition(
                name="statistics_calc",
                description="统计计算",
                function=CalculationTools.statistics_calc,
                parameters=[
                    ToolParameter("numbers", "array", "数字列表", True),
                    ToolParameter("operation", "string", "统计操作(mean/median/sum/max/min)", False, "mean")
                ],
                tool_type=ToolType.CALCULATION,
                examples=["计算平均值", "求最大最小值"],
                tags=["统计", "数学", "分析"]
            ),
            ToolDefinition(
                name="unit_conversion",
                description="单位转换",
                function=CalculationTools.unit_conversion,
                parameters=[
                    ToolParameter("value", "number", "数值", True),
                    ToolParameter("from_unit", "string", "源单位", True),
                    ToolParameter("to_unit", "string", "目标单位", True),
                    ToolParameter("unit_type", "string", "单位类型(length/weight/temperature)", False, "length")
                ],
                tool_type=ToolType.CALCULATION,
                examples=["米转换为英尺", "摄氏度转华氏度"],
                tags=["转换", "单位", "计算"]
            )
        ])
        
        # 文本处理工具
        tools.extend([
            ToolDefinition(
                name="text_analysis",
                description="分析文本统计信息",
                function=TextProcessingTools.text_analysis,
                parameters=[
                    ToolParameter("text", "string", "要分析的文本", True)
                ],
                tool_type=ToolType.TEXT_PROCESSING,
                examples=["分析文章字数", "统计文本信息"],
                tags=["文本", "分析", "统计"]
            ),
            ToolDefinition(
                name="text_search_replace",
                description="文本搜索替换",
                function=TextProcessingTools.text_search_replace,
                parameters=[
                    ToolParameter("text", "string", "原始文本", True),
                    ToolParameter("search_pattern", "string", "搜索模式", True),
                    ToolParameter("replacement", "string", "替换内容", True),
                    ToolParameter("use_regex", "boolean", "使用正则表达式", False, False)
                ],
                tool_type=ToolType.TEXT_PROCESSING,
                examples=["替换文本中的特定词汇", "批量修改格式"],
                tags=["文本", "替换", "搜索"]
            ),
            ToolDefinition(
                name="text_hash",
                description="计算文本哈希值",
                function=TextProcessingTools.text_hash,
                parameters=[
                    ToolParameter("text", "string", "要计算哈希的文本", True),
                    ToolParameter("algorithm", "string", "哈希算法(md5/sha1/sha256)", False, "md5")
                ],
                tool_type=ToolType.TEXT_PROCESSING,
                examples=["生成文件校验码", "计算密码哈希"],
                tags=["哈希", "加密", "校验"]
            )
        ])
        
        return tools
    
    @staticmethod
    def register_all_tools(agent) -> None:
        """将所有预定义工具注册到智能体"""
        tools = PredefinedToolsRegistry.get_all_tools()
        for tool in tools:
            agent.register_tool(tool)
        
        print(f"✅ 已注册 {len(tools)} 个预定义工具")
