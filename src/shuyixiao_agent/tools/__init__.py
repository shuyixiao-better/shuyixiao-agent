"""
工具模块

包含各种可供 Agent 使用的工具
"""

from .basic_tools import (
    get_current_time, 
    calculate, 
    search_wikipedia,
    get_random_number,
    convert_temperature,
    string_reverse,
    count_words,
    get_date_info,
    calculate_age,
    generate_uuid,
    encode_base64,
    decode_base64,
    check_prime,
    get_basic_tools
)

from .ai_powered_tools import (
    web_content_analyzer,
    text_quality_analyzer,
    creative_idea_generator,
    code_review_assistant,
    decision_analyzer,
    data_insight_generator,
    content_improver,
    problem_solver,
    meeting_summarizer,
    learning_path_designer,
    get_ai_powered_tools
)

__all__ = [
    # 基础工具（简单的硬编码逻辑）
    "get_current_time", 
    "calculate", 
    "search_wikipedia",
    "get_random_number",
    "convert_temperature",
    "string_reverse",
    "count_words",
    "get_date_info",
    "calculate_age",
    "generate_uuid",
    "encode_base64",
    "decode_base64",
    "check_prime",
    "get_basic_tools",
    
    # AI驱动的智能工具（需要大模型参与）
    "web_content_analyzer",
    "text_quality_analyzer",
    "creative_idea_generator",
    "code_review_assistant",
    "decision_analyzer",
    "data_insight_generator",
    "content_improver",
    "problem_solver",
    "meeting_summarizer",
    "learning_path_designer",
    "get_ai_powered_tools"
]

