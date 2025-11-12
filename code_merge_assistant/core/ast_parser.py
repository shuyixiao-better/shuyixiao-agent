"""AST 语法树解析模块（用于更智能的代码分析）"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CodeBlock:
    """代码块"""
    type: str  # class, method, function, import, comment
    name: str
    start_line: int
    end_line: int
    content: str
    signature: str = ""  # 方法签名


class SimpleASTParser:
    """
    简化的 AST 解析器
    支持 Java, Python, JavaScript 等常见语言
    """
    
    def __init__(self, language: str = "auto"):
        self.language = language
        self.blocks: List[CodeBlock] = []
    
    def parse(self, code: str) -> List[CodeBlock]:
        """
        解析代码，提取关键代码块
        
        Args:
            code: 源代码
            
        Returns:
            代码块列表
        """
        if self.language == "auto":
            self.language = self._detect_language(code)
        
        lines = code.split('\n')
        
        if self.language == "java":
            return self._parse_java(lines)
        elif self.language == "python":
            return self._parse_python(lines)
        elif self.language == "javascript":
            return self._parse_javascript(lines)
        else:
            return self._parse_generic(lines)
    
    def _detect_language(self, code: str) -> str:
        """自动检测编程语言"""
        if re.search(r'\bpublic\s+class\b|\bprivate\s+\w+\s+\w+\(', code):
            return "java"
        elif re.search(r'\bdef\s+\w+\(|\bclass\s+\w+:', code):
            return "python"
        elif re.search(r'\bfunction\s+\w+\(|\bconst\s+\w+\s*=|\blet\s+\w+\s*=', code):
            return "javascript"
        return "generic"
    
    def _parse_java(self, lines: List[str]) -> List[CodeBlock]:
        """解析 Java 代码"""
        blocks = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 导入语句
            if stripped.startswith('import '):
                blocks.append(CodeBlock(
                    type="import",
                    name=stripped,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
            
            # 类定义
            class_match = re.match(r'.*\b(public|private|protected)?\s*class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(2)
                blocks.append(CodeBlock(
                    type="class",
                    name=class_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
            
            # 方法定义
            method_match = re.match(
                r'.*\b(public|private|protected)?\s*(static)?\s*(\w+)\s+(\w+)\s*\([^)]*\)',
                stripped
            )
            if method_match and not stripped.startswith('//'):
                method_name = method_match.group(4)
                blocks.append(CodeBlock(
                    type="method",
                    name=method_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line,
                    signature=stripped
                ))
        
        return blocks
    
    def _parse_python(self, lines: List[str]) -> List[CodeBlock]:
        """解析 Python 代码"""
        blocks = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 导入语句
            if stripped.startswith('import ') or stripped.startswith('from '):
                blocks.append(CodeBlock(
                    type="import",
                    name=stripped,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
            
            # 类定义
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                blocks.append(CodeBlock(
                    type="class",
                    name=class_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
            
            # 函数/方法定义
            func_match = re.match(r'def\s+(\w+)\s*\([^)]*\)', stripped)
            if func_match:
                func_name = func_match.group(1)
                blocks.append(CodeBlock(
                    type="function",
                    name=func_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line,
                    signature=stripped
                ))
        
        return blocks
    
    def _parse_javascript(self, lines: List[str]) -> List[CodeBlock]:
        """解析 JavaScript 代码"""
        blocks = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 导入语句
            if stripped.startswith('import ') or stripped.startswith('require('):
                blocks.append(CodeBlock(
                    type="import",
                    name=stripped,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
            
            # 类定义
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                blocks.append(CodeBlock(
                    type="class",
                    name=class_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
            
            # 函数定义
            func_match = re.match(r'function\s+(\w+)\s*\([^)]*\)', stripped)
            if func_match:
                func_name = func_match.group(1)
                blocks.append(CodeBlock(
                    type="function",
                    name=func_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line,
                    signature=stripped
                ))
            
            # 箭头函数
            arrow_match = re.match(r'(const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>', stripped)
            if arrow_match:
                func_name = arrow_match.group(2)
                blocks.append(CodeBlock(
                    type="function",
                    name=func_name,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line,
                    signature=stripped
                ))
        
        return blocks
    
    def _parse_generic(self, lines: List[str]) -> List[CodeBlock]:
        """通用解析（适用于未知语言）"""
        blocks = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测可能的函数定义（通用模式）
            if '(' in stripped and ')' in stripped and '{' in stripped:
                blocks.append(CodeBlock(
                    type="block",
                    name=f"Line {i+1}",
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line
                ))
        
        return blocks
    
    def compare_blocks(self, base_blocks: List[CodeBlock], 
                      incoming_blocks: List[CodeBlock]) -> Dict:
        """
        对比两组代码块，找出新增、删除、修改的部分
        
        Returns:
            对比结果字典
        """
        base_dict = {block.name: block for block in base_blocks}
        incoming_dict = {block.name: block for block in incoming_blocks}
        
        added = []
        deleted = []
        modified = []
        
        # 找出新增的
        for name, block in incoming_dict.items():
            if name not in base_dict:
                added.append(block)
            elif base_dict[name].signature != block.signature:
                modified.append({
                    'base': base_dict[name],
                    'incoming': block
                })
        
        # 找出删除的
        for name, block in base_dict.items():
            if name not in incoming_dict:
                deleted.append(block)
        
        return {
            'added': added,
            'deleted': deleted,
            'modified': modified
        }
