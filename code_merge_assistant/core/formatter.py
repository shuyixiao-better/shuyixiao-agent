"""输出格式化模块"""

from typing import Dict, List
from colorama import Fore, Back, Style, init
from .diff_engine import CodeChange, ChangeType

# 初始化 colorama（Windows 支持）
init(autoreset=True)


class ConsoleFormatter:
    """控制台输出格式化器"""
    
    @staticmethod
    def format_diff(analysis_result: Dict) -> str:
        """
        格式化差异分析结果为彩色控制台输出
        
        Args:
            analysis_result: 差异分析结果
            
        Returns:
            格式化后的文本
        """
        output = []
        
        # 标题
        output.append("\n" + "=" * 60)
        output.append(f"{Fore.CYAN}📊 代码差异分析报告{Style.RESET_ALL}")
        output.append("=" * 60 + "\n")
        
        # 统计摘要
        output.append(f"{Fore.YELLOW}📈 变更统计：{Style.RESET_ALL}")
        output.append(analysis_result["summary"])
        output.append("\n" + "-" * 60 + "\n")
        
        # 详细差异
        output.append(f"{Fore.YELLOW}🔍 详细差异：{Style.RESET_ALL}\n")
        
        changes: List[CodeChange] = analysis_result["changes"]
        
        for change in changes:
            if change.change_type == ChangeType.ADD:
                output.append(
                    f"{Fore.GREEN}+ [行 {change.line_num_incoming}] "
                    f"{change.content_incoming.rstrip()}{Style.RESET_ALL}"
                )
            elif change.change_type == ChangeType.DELETE:
                output.append(
                    f"{Fore.RED}- [行 {change.line_num_base}] "
                    f"{change.content_base.rstrip()}{Style.RESET_ALL}"
                )
            elif change.change_type == ChangeType.MODIFY:
                output.append(
                    f"{Fore.YELLOW}⚠ [行 {change.line_num_base} → {change.line_num_incoming}]{Style.RESET_ALL}"
                )
                output.append(
                    f"{Fore.RED}  - {change.content_base.rstrip()}{Style.RESET_ALL}"
                )
                output.append(
                    f"{Fore.GREEN}  + {change.content_incoming.rstrip()}{Style.RESET_ALL}"
                )
        
        output.append("\n" + "=" * 60 + "\n")
        
        return "\n".join(output)
    
    @staticmethod
    def format_side_by_side(base_code: str, incoming_code: str, 
                           changes: List[CodeChange]) -> str:
        """
        生成并排对比视图
        
        Args:
            base_code: 基准代码
            incoming_code: 新代码
            changes: 变更列表
            
        Returns:
            并排对比文本
        """
        base_lines = base_code.splitlines()
        incoming_lines = incoming_code.splitlines()
        
        output = []
        output.append("\n" + "=" * 120)
        output.append(f"{Fore.CYAN}📋 并排对比视图{Style.RESET_ALL}")
        output.append("=" * 120)
        
        # 表头
        header = f"{'基准版本':<50} | {'新版本':<50}"
        output.append(f"{Fore.YELLOW}{header}{Style.RESET_ALL}")
        output.append("-" * 120)
        
        # 构建变更映射
        change_map = {}
        for change in changes:
            if change.change_type == ChangeType.MODIFY:
                change_map[change.line_num_base - 1] = change
        
        max_lines = max(len(base_lines), len(incoming_lines))
        
        for i in range(max_lines):
            base_line = base_lines[i] if i < len(base_lines) else ""
            incoming_line = incoming_lines[i] if i < len(incoming_lines) else ""
            
            # 检查是否有变更
            if i in change_map:
                change = change_map[i]
                base_part = f"{Fore.RED}{base_line[:47]:<47}{Style.RESET_ALL}"
                incoming_part = f"{Fore.GREEN}{incoming_line[:47]:<47}{Style.RESET_ALL}"
                output.append(f"{base_part} | {incoming_part}")
            else:
                output.append(f"{base_line[:50]:<50} | {incoming_line[:50]:<50}")
        
        output.append("=" * 120 + "\n")
        
        return "\n".join(output)


class HTMLFormatter:
    """HTML 输出格式化器（用于 Web 界面）"""
    
    @staticmethod
    def format_diff(analysis_result: Dict) -> str:
        """
        格式化差异分析结果为 HTML
        
        Args:
            analysis_result: 差异分析结果
            
        Returns:
            HTML 格式的差异报告
        """
        html = ['<div class="diff-report">']
        
        # 统计摘要
        html.append('<div class="summary">')
        html.append('<h3>📈 变更统计</h3>')
        html.append(f'<pre>{analysis_result["summary"]}</pre>')
        html.append('</div>')
        
        # 详细差异
        html.append('<div class="details">')
        html.append('<h3>🔍 详细差异</h3>')
        html.append('<div class="diff-content">')
        
        changes: List[CodeChange] = analysis_result["changes"]
        
        for change in changes:
            if change.change_type == ChangeType.ADD:
                html.append(
                    f'<div class="line-add">'
                    f'<span class="line-num">{change.line_num_incoming}</span>'
                    f'<span class="line-content">+ {change.content_incoming.rstrip()}</span>'
                    f'</div>'
                )
            elif change.change_type == ChangeType.DELETE:
                html.append(
                    f'<div class="line-delete">'
                    f'<span class="line-num">{change.line_num_base}</span>'
                    f'<span class="line-content">- {change.content_base.rstrip()}</span>'
                    f'</div>'
                )
            elif change.change_type == ChangeType.MODIFY:
                html.append(
                    f'<div class="line-modify">'
                    f'<div class="line-delete">'
                    f'<span class="line-num">{change.line_num_base}</span>'
                    f'<span class="line-content">- {change.content_base.rstrip()}</span>'
                    f'</div>'
                    f'<div class="line-add">'
                    f'<span class="line-num">{change.line_num_incoming}</span>'
                    f'<span class="line-content">+ {change.content_incoming.rstrip()}</span>'
                    f'</div>'
                    f'</div>'
                )
        
        html.append('</div>')
        html.append('</div>')
        html.append('</div>')
        
        return '\n'.join(html)
