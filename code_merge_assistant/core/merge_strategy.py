"""合并策略模块"""

from typing import Dict, List
from .diff_engine import CodeChange, ChangeType
from .ast_parser import SimpleASTParser, CodeBlock


class MergeStrategy:
    """合并策略引擎"""
    
    def __init__(self):
        self.parser = SimpleASTParser()
    
    def analyze_with_context(self, base_code: str, incoming_code: str) -> Dict:
        """
        带上下文的智能分析
        
        Args:
            base_code: 基准代码
            incoming_code: 新代码
            
        Returns:
            增强的分析结果
        """
        # 解析代码块
        base_blocks = self.parser.parse(base_code)
        incoming_blocks = self.parser.parse(incoming_code)
        
        # 对比代码块
        block_diff = self.parser.compare_blocks(base_blocks, incoming_blocks)
        
        # 生成建议
        suggestions = self._generate_suggestions(block_diff)
        
        return {
            'base_blocks': base_blocks,
            'incoming_blocks': incoming_blocks,
            'block_diff': block_diff,
            'suggestions': suggestions
        }
    
    def _generate_suggestions(self, block_diff: Dict) -> List[Dict]:
        """生成合并建议"""
        suggestions = []
        
        # 新增的代码块
        for block in block_diff['added']:
            if block.type == 'method' or block.type == 'function':
                suggestions.append({
                    'type': 'accept',
                    'target': block.name,
                    'message': f"✅ 新增{block.type} `{block.name}`，建议接受",
                    'priority': 'high'
                })
            elif block.type == 'import':
                suggestions.append({
                    'type': 'accept',
                    'target': block.name,
                    'message': f"✅ 新增导入语句，建议接受",
                    'priority': 'medium'
                })
        
        # 删除的代码块
        for block in block_diff['deleted']:
            if block.type == 'method' or block.type == 'function':
                suggestions.append({
                    'type': 'review',
                    'target': block.name,
                    'message': f"⚠️  删除{block.type} `{block.name}`，需要确认是否必要",
                    'priority': 'high'
                })
        
        # 修改的代码块
        for item in block_diff['modified']:
            base_block = item['base']
            incoming_block = item['incoming']
            suggestions.append({
                'type': 'review',
                'target': base_block.name,
                'message': f"⚠️  修改{base_block.type} `{base_block.name}`，需要人工审查",
                'priority': 'high',
                'details': {
                    'base_signature': base_block.signature,
                    'incoming_signature': incoming_block.signature
                }
            })
        
        return suggestions
    
    def format_suggestions(self, suggestions: List[Dict]) -> str:
        """格式化建议为可读文本"""
        if not suggestions:
            return "✅ 没有需要特别注意的变更"
        
        output = ["💡 合并建议：\n"]
        
        # 按优先级分组
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        medium_priority = [s for s in suggestions if s['priority'] == 'medium']
        
        if high_priority:
            output.append("【高优先级】")
            for s in high_priority:
                output.append(f"  {s['message']}")
                if 'details' in s:
                    output.append(f"    原签名: {s['details']['base_signature']}")
                    output.append(f"    新签名: {s['details']['incoming_signature']}")
            output.append("")
        
        if medium_priority:
            output.append("【中优先级】")
            for s in medium_priority:
                output.append(f"  {s['message']}")
            output.append("")
        
        return "\n".join(output)
