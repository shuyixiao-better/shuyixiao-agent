#!/usr/bin/env python3
"""代码合并辅助工具 - Web 界面"""

from flask import Flask, render_template, request, jsonify
from core.diff_engine import DiffEngine
from core.formatter import HTMLFormatter, ConsoleFormatter

app = Flask(__name__)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/compare', methods=['POST'])
def compare():
    """代码对比 API"""
    try:
        data = request.get_json()
        base_code = data.get('base_code', '')
        incoming_code = data.get('incoming_code', '')
        
        if not base_code or not incoming_code:
            return jsonify({
                'success': False,
                'error': '请输入两段代码'
            }), 400
        
        # 执行差异分析
        engine = DiffEngine()
        result = engine.analyze(base_code, incoming_code)
        
        # 格式化为 HTML
        html_formatter = HTMLFormatter()
        html_output = html_formatter.format_diff(result)
        
        # 生成统一 diff
        unified_diff = engine.get_unified_diff(base_code, incoming_code)
        
        return jsonify({
            'success': True,
            'html': html_output,
            'summary': result['summary'],
            'stats': result['stats'],
            'unified_diff': unified_diff,
            'total_changes': len(result['changes'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 代码合并辅助工具 Web 界面启动中...")
    print("📍 访问地址: http://localhost:5678")
    print("💡 提示: 按 Ctrl+C 停止服务")
    print("-" * 60)
    
    app.run(host='0.0.0.0', port=5678, debug=True)
