"""差异分析引擎"""

import difflib
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    """变更类型"""
    ADD = "add"
    DELETE = "delete"
    MODIFY = "modify"
    UNCHANGED = "unchanged"


@dataclass
class CodeChange:
    """代码变更记录"""
    change_type: ChangeType
    line_num_base: int
    line_num_incoming: int
    content_base: str
    content_incoming: str
    context: str = ""  # 上下文信息（如所属类、方法）


class DiffEngine:
    """差异分析引擎"""
    
    def __init__(self):
        self.changes: List[CodeChange] = []
        self.stats = {
            "added_lines": 0,
            "deleted_lines": 0,
            "modified_lines": 0,
            "unchanged_lines": 0
        }
    
    def analyze(self, base_code: str, incoming_code: str) -> Dict:
        """
        分析两段代码的差异
        
        Args:
            base_code: 基准代码（你的版本）
            incoming_code: 传入代码（同事的版本）
            
        Returns:
            差异分析结果
        """
        base_lines = base_code.splitlines(keepends=True)
        incoming_lines = incoming_code.splitlines(keepends=True)
        
        # 使用 difflib 进行差异对比
        differ = difflib.Differ()
        diff = list(differ.compare(base_lines, incoming_lines))
        
        self._parse_diff(diff, base_lines, incoming_lines)
        
        return {
            "changes": self.changes,
            "stats": self.stats,
            "summary": self._generate_summary()
        }
    
    def _parse_diff(self, diff: List[str], base_lines: List[str], incoming_lines: List[str]):
        """解析 diff 结果"""
        self.changes = []
        base_idx = 0
        incoming_idx = 0
        
        i = 0
        while i < len(diff):
            line = diff[i]
            
            if line.startswith('  '):  # 未变更
                self.stats["unchanged_lines"] += 1
                base_idx += 1
                incoming_idx += 1
                
            elif line.startswith('- '):  # 删除
                # 检查是否是修改（后面紧跟 +）
                if i + 1 < len(diff) and diff[i + 1].startswith('+ '):
                    # 这是修改
                    change = CodeChange(
                        change_type=ChangeType.MODIFY,
                        line_num_base=base_idx + 1,
                        line_num_incoming=incoming_idx + 1,
                        content_base=line[2:],
                        content_incoming=diff[i + 1][2:]
                    )
                    self.changes.append(change)
                    self.stats["modified_lines"] += 1
                    base_idx += 1
                    incoming_idx += 1
                    i += 1  # 跳过下一行
                else:
                    # 纯删除
                    change = CodeChange(
                        change_type=ChangeType.DELETE,
                        line_num_base=base_idx + 1,
                        line_num_incoming=-1,
                        content_base=line[2:],
                        content_incoming=""
                    )
                    self.changes.append(change)
                    self.stats["deleted_lines"] += 1
                    base_idx += 1
                    
            elif line.startswith('+ '):  # 新增
                change = CodeChange(
                    change_type=ChangeType.ADD,
                    line_num_base=-1,
                    line_num_incoming=incoming_idx + 1,
                    content_base="",
                    content_incoming=line[2:]
                )
                self.changes.append(change)
                self.stats["added_lines"] += 1
                incoming_idx += 1
                
            elif line.startswith('? '):  # 差异标记行，跳过
                pass
                
            i += 1
    
    def _generate_summary(self) -> str:
        """生成差异摘要"""
        total_changes = (
            self.stats["added_lines"] + 
            self.stats["deleted_lines"] + 
            self.stats["modified_lines"]
        )
        
        summary = f"共发现 {total_changes} 处变更：\n"
        summary += f"  • 新增：{self.stats['added_lines']} 行\n"
        summary += f"  • 删除：{self.stats['deleted_lines']} 行\n"
        summary += f"  • 修改：{self.stats['modified_lines']} 行\n"
        summary += f"  • 未变更：{self.stats['unchanged_lines']} 行"
        
        return summary
    
    def get_unified_diff(self, base_code: str, incoming_code: str, 
                        base_name: str = "基准版本", 
                        incoming_name: str = "新版本") -> str:
        """
        生成统一格式的 diff（类似 git diff）
        
        Returns:
            统一格式的差异文本
        """
        base_lines = base_code.splitlines(keepends=True)
        incoming_lines = incoming_code.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            base_lines,
            incoming_lines,
            fromfile=base_name,
            tofile=incoming_name,
            lineterm=''
        )
        
        return ''.join(diff)
