"""
AI驱动的智能工具集

这些工具真正需要大模型的理解、推理和生成能力，
而不是简单的硬编码逻辑。
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re
from datetime import datetime


def web_content_analyzer(url: str, analysis_type: str = "summary") -> Dict:
    """
    智能网页内容分析器
    
    需要AI能力：
    - 理解网页内容的主题和结构
    - 提取关键信息
    - 生成有意义的摘要
    
    Args:
        url: 要分析的网页URL
        analysis_type: 分析类型 (summary/keywords/sentiment/structure)
        
    Returns:
        包含分析结果的字典，需要AI进一步处理原始内容
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取主要内容
        title = soup.find('title').text if soup.find('title') else "无标题"
        
        # 提取所有段落文本
        paragraphs = []
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'article']):
            text = p.get_text(strip=True)
            if len(text) > 20:  # 过滤太短的段落
                paragraphs.append(text)
        
        content = "\n".join(paragraphs[:50])  # 限制内容长度
        
        # 返回原始内容，让AI进行智能分析
        return {
            "url": url,
            "title": title,
            "raw_content": content[:3000],  # 限制长度
            "analysis_type": analysis_type,
            "instruction": f"请对以下网页内容进行{analysis_type}分析：\n\n标题：{title}\n\n内容：\n{content[:2000]}",
            "content_length": len(content),
            "paragraph_count": len(paragraphs),
            "needs_ai_processing": True
        }
    except Exception as e:
        return {
            "error": f"抓取失败: {str(e)}",
            "needs_ai_processing": False
        }


def text_quality_analyzer(text: str) -> Dict:
    """
    文本质量智能分析器
    
    需要AI能力：
    - 判断文本的连贯性和逻辑性
    - 发现语法和表达问题
    - 提供改进建议
    
    Args:
        text: 要分析的文本
        
    Returns:
        包含原始文本的字典，需要AI进行质量分析
    """
    # 基础统计（非AI部分）
    word_count = len(text.split())
    sentence_count = len([s for s in text.split('.') if s.strip()])
    
    return {
        "original_text": text,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "instruction": f"""请作为专业的文本编辑，分析以下文本的质量并提供改进建议：

原文：
{text}

请从以下几个维度分析：
1. 语言表达：是否流畅、准确、简洁
2. 逻辑结构：是否清晰、连贯、有条理
3. 语法错误：是否存在语法、标点、用词问题
4. 改进建议：具体的修改建议和改写示例

请给出专业的分析报告。""",
        "needs_ai_processing": True
    }


def creative_idea_generator(topic: str, idea_type: str = "general", count: int = 5) -> Dict:
    """
    创意想法生成器
    
    需要AI能力：
    - 发散性思维
    - 创新性思考
    - 结合常识和创意
    
    Args:
        topic: 主题
        idea_type: 想法类型 (business/product/marketing/content/solution)
        count: 生成数量
        
    Returns:
        包含生成指令的字典
    """
    type_descriptions = {
        "business": "商业模式创意",
        "product": "产品功能创意", 
        "marketing": "营销推广创意",
        "content": "内容创作创意",
        "solution": "问题解决方案"
    }
    
    description = type_descriptions.get(idea_type, "创意想法")
    
    return {
        "topic": topic,
        "idea_type": idea_type,
        "count": count,
        "instruction": f"""请为"{topic}"主题生成{count}个有创意的{description}。

要求：
1. 每个创意都要具有创新性和可行性
2. 提供具体的实施思路
3. 说明创意的价值和优势
4. 考虑实际应用场景

请以结构化的方式呈现，包含创意标题、详细描述、实施要点和预期效果。""",
        "needs_ai_processing": True
    }


def code_review_assistant(code: str, language: str = "python") -> Dict:
    """
    代码智能审查助手
    
    需要AI能力：
    - 理解代码逻辑
    - 发现潜在问题
    - 提供优化建议
    - 评估代码质量
    
    Args:
        code: 要审查的代码
        language: 编程语言
        
    Returns:
        包含代码和审查指令的字典
    """
    return {
        "code": code,
        "language": language,
        "instruction": f"""请作为资深工程师，对以下{language}代码进行专业的代码审查：

```{language}
{code}
```

请从以下维度进行审查：

1. **代码质量**
   - 可读性和可维护性
   - 命名规范
   - 代码结构

2. **潜在问题**
   - Bug和逻辑错误
   - 安全隐患
   - 性能问题
   - 边界条件处理

3. **最佳实践**
   - 是否符合语言习惯
   - 设计模式应用
   - 异常处理

4. **优化建议**
   - 具体的改进方案
   - 优化后的代码示例

请给出详细的审查报告和改进建议。""",
        "needs_ai_processing": True
    }


def decision_analyzer(situation: str, options: List[str]) -> Dict:
    """
    决策智能分析器
    
    需要AI能力：
    - 多角度分析问题
    - 权衡利弊
    - 提供理性建议
    
    Args:
        situation: 决策场景描述
        options: 可选方案列表
        
    Returns:
        包含决策分析指令的字典
    """
    options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    
    return {
        "situation": situation,
        "options": options,
        "instruction": f"""请作为决策顾问，帮助分析以下决策场景：

**场景描述：**
{situation}

**可选方案：**
{options_text}

请提供专业的决策分析：

1. **场景分析**
   - 关键因素识别
   - 潜在风险和机会

2. **方案对比**
   - 每个方案的优劣势
   - 适用场景
   - 风险评估

3. **综合建议**
   - 推荐方案及理由
   - 实施建议
   - 注意事项

请给出理性、全面的决策分析。""",
        "needs_ai_processing": True
    }


def data_insight_generator(data_description: str, data_sample: str) -> Dict:
    """
    数据洞察生成器
    
    需要AI能力：
    - 理解数据含义
    - 发现数据规律和趋势
    - 提供有价值的洞察
    
    Args:
        data_description: 数据描述
        data_sample: 数据样本（文本形式）
        
    Returns:
        包含数据和分析指令的字典
    """
    return {
        "data_description": data_description,
        "data_sample": data_sample,
        "instruction": f"""请作为数据分析师，对以下数据进行深入分析：

**数据描述：**
{data_description}

**数据样本：**
{data_sample}

请提供数据洞察分析：

1. **数据理解**
   - 数据的含义和背景
   - 关键指标识别

2. **趋势分析**
   - 发现的模式和规律
   - 异常值和特殊情况

3. **深度洞察**
   - 数据背后的故事
   - 可能的原因分析
   - 业务价值和意义

4. **行动建议**
   - 基于数据的决策建议
   - 需要关注的重点

请提供专业、有洞察力的分析报告。""",
        "needs_ai_processing": True
    }


def content_improver(content: str, improvement_type: str = "general") -> Dict:
    """
    内容智能优化器
    
    需要AI能力：
    - 理解内容意图
    - 优化表达方式
    - 提升内容质量
    
    Args:
        content: 原始内容
        improvement_type: 优化类型 (general/professional/casual/persuasive)
        
    Returns:
        包含内容和优化指令的字典
    """
    type_instructions = {
        "general": "提升整体质量，使表达更清晰、更有说服力",
        "professional": "改写为更专业、更正式的商务风格",
        "casual": "改写为更轻松、更易读的口语化风格",
        "persuasive": "增强说服力，让内容更有感染力"
    }
    
    instruction_detail = type_instructions.get(improvement_type, type_instructions["general"])
    
    return {
        "original_content": content,
        "improvement_type": improvement_type,
        "instruction": f"""请帮助优化以下内容，优化方向：{instruction_detail}

**原始内容：**
{content}

请提供：

1. **优化后的内容**
   - 完整的改写版本
   - 保留原意，提升表达

2. **改进说明**
   - 主要改进点
   - 优化的理由
   - 前后对比分析

3. **额外建议**
   - 进一步改进的空间
   - 适用场景建议

请提供高质量的优化结果。""",
        "needs_ai_processing": True
    }


def problem_solver(problem: str, context: str = "") -> Dict:
    """
    智能问题解决器
    
    需要AI能力：
    - 理解问题本质
    - 分解复杂问题
    - 提供系统性解决方案
    
    Args:
        problem: 问题描述
        context: 背景信息
        
    Returns:
        包含问题和求解指令的字典
    """
    context_text = f"\n\n**背景信息：**\n{context}" if context else ""
    
    return {
        "problem": problem,
        "context": context,
        "instruction": f"""请作为问题解决专家，帮助分析和解决以下问题：

**问题描述：**
{problem}{context_text}

请提供系统性的解决方案：

1. **问题分析**
   - 问题的核心是什么
   - 关键挑战和制约因素
   - 相关的子问题

2. **解决思路**
   - 可能的解决方向（列举多个）
   - 每个方向的可行性分析

3. **推荐方案**
   - 最佳解决方案
   - 具体实施步骤
   - 所需资源和条件

4. **风险和应对**
   - 可能的困难
   - 应对措施

请提供详细、可行的解决方案。""",
        "needs_ai_processing": True
    }


def meeting_summarizer(meeting_notes: str) -> Dict:
    """
    会议智能总结器
    
    需要AI能力：
    - 理解会议内容
    - 提取关键信息
    - 结构化呈现
    
    Args:
        meeting_notes: 会议记录或录音转文字
        
    Returns:
        包含会议内容和总结指令的字典
    """
    return {
        "meeting_notes": meeting_notes,
        "instruction": f"""请作为会议助理，对以下会议内容进行智能总结：

**会议记录：**
{meeting_notes}

请提供结构化的会议总结：

1. **会议概要**
   - 会议主题
   - 参与人员（如有）
   - 会议时长（如有）

2. **讨论要点**
   - 主要讨论的议题
   - 每个议题的关键观点
   - 达成的共识

3. **决策事项**
   - 明确的决定
   - 需要执行的行动

4. **待办任务**
   - 任务清单
   - 负责人（如有）
   - 截止时间（如有）

5. **遗留问题**
   - 未解决的问题
   - 需要跟进的事项

请提供清晰、完整的会议总结。""",
        "needs_ai_processing": True
    }


def learning_path_designer(topic: str, current_level: str = "beginner", goal: str = "") -> Dict:
    """
    学习路径设计器
    
    需要AI能力：
    - 理解知识体系
    - 设计学习路径
    - 提供个性化建议
    
    Args:
        topic: 学习主题
        current_level: 当前水平 (beginner/intermediate/advanced)
        goal: 学习目标
        
    Returns:
        包含学习路径设计指令的字典
    """
    level_desc = {
        "beginner": "零基础新手",
        "intermediate": "有一定基础",
        "advanced": "进阶学习者"
    }
    
    current_desc = level_desc.get(current_level, "初学者")
    goal_text = f"\n\n**学习目标：**\n{goal}" if goal else ""
    
    return {
        "topic": topic,
        "current_level": current_level,
        "goal": goal,
        "instruction": f"""请作为学习顾问，为"{topic}"设计一个系统的学习路径：

**当前水平：**{current_desc}{goal_text}

请提供详细的学习路径规划：

1. **知识体系**
   - 该领域的核心知识点
   - 知识模块和层级关系

2. **学习路径**
   - 分阶段的学习计划
   - 每个阶段的学习重点
   - 预估学习时间

3. **学习资源**
   - 推荐的学习资料（书籍、课程、网站等）
   - 实践项目建议
   - 学习工具推荐

4. **学习建议**
   - 学习方法和技巧
   - 常见误区和避坑指南
   - 检验学习成果的方式

5. **进阶方向**
   - 深入学习的方向
   - 相关领域拓展

请提供实用、系统的学习路径。""",
        "needs_ai_processing": True
    }


# 工具定义（用于注册到 Agent）
AI_POWERED_TOOL_DEFINITIONS = {
    "web_content_analyzer": {
        "name": "web_content_analyzer",
        "description": "智能网页内容分析器。抓取网页并进行深度分析，包括内容摘要、关键词提取、情感分析等。需要AI的理解和分析能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要分析的网页URL"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "分析类型：summary(摘要)/keywords(关键词)/sentiment(情感)/structure(结构)，默认为summary"
                }
            },
            "required": ["url"]
        }
    },
    "text_quality_analyzer": {
        "name": "text_quality_analyzer",
        "description": "文本质量智能分析器。分析文本的语言表达、逻辑结构、语法错误，并提供专业的改进建议。需要AI的语言理解和评估能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要分析的文本内容"
                }
            },
            "required": ["text"]
        }
    },
    "creative_idea_generator": {
        "name": "creative_idea_generator",
        "description": "创意想法生成器。为特定主题生成创新性的想法，包括商业模式、产品功能、营销方案等。需要AI的创造力和发散思维。",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "创意主题"
                },
                "idea_type": {
                    "type": "string",
                    "description": "想法类型：business(商业)/product(产品)/marketing(营销)/content(内容)/solution(解决方案)，默认为general"
                },
                "count": {
                    "type": "integer",
                    "description": "生成数量，默认为5"
                }
            },
            "required": ["topic"]
        }
    },
    "code_review_assistant": {
        "name": "code_review_assistant",
        "description": "代码智能审查助手。对代码进行专业审查，发现潜在问题、提供优化建议和改进方案。需要AI的代码理解和工程经验。",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要审查的代码"
                },
                "language": {
                    "type": "string",
                    "description": "编程语言，如python/java/javascript等，默认为python"
                }
            },
            "required": ["code"]
        }
    },
    "decision_analyzer": {
        "name": "decision_analyzer",
        "description": "决策智能分析器。分析决策场景，对比各个方案的优劣，提供理性的决策建议。需要AI的多维度分析和推理能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "situation": {
                    "type": "string",
                    "description": "决策场景描述"
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "可选方案列表"
                }
            },
            "required": ["situation", "options"]
        }
    },
    "data_insight_generator": {
        "name": "data_insight_generator",
        "description": "数据洞察生成器。分析数据样本，发现规律和趋势，提供有价值的数据洞察。需要AI的数据理解和分析能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "data_description": {
                    "type": "string",
                    "description": "数据描述"
                },
                "data_sample": {
                    "type": "string",
                    "description": "数据样本（文本形式）"
                }
            },
            "required": ["data_description", "data_sample"]
        }
    },
    "content_improver": {
        "name": "content_improver",
        "description": "内容智能优化器。优化文本内容的表达方式，提升内容质量。支持多种风格转换。需要AI的语言生成和改写能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "原始内容"
                },
                "improvement_type": {
                    "type": "string",
                    "description": "优化类型：general(通用)/professional(专业)/casual(轻松)/persuasive(说服)，默认为general"
                }
            },
            "required": ["content"]
        }
    },
    "problem_solver": {
        "name": "problem_solver",
        "description": "智能问题解决器。分析复杂问题，提供系统性的解决方案和实施步骤。需要AI的问题分解和推理能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "问题描述"
                },
                "context": {
                    "type": "string",
                    "description": "背景信息（可选）"
                }
            },
            "required": ["problem"]
        }
    },
    "meeting_summarizer": {
        "name": "meeting_summarizer",
        "description": "会议智能总结器。将会议记录转换为结构化的会议总结，包括讨论要点、决策事项、待办任务等。需要AI的信息提取和结构化能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_notes": {
                    "type": "string",
                    "description": "会议记录或录音转文字"
                }
            },
            "required": ["meeting_notes"]
        }
    },
    "learning_path_designer": {
        "name": "learning_path_designer",
        "description": "学习路径设计器。为特定主题设计系统的学习路径，包括知识体系、学习资源、实践建议等。需要AI的知识整合和规划能力。",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "学习主题"
                },
                "current_level": {
                    "type": "string",
                    "description": "当前水平：beginner(初学者)/intermediate(中级)/advanced(高级)，默认为beginner"
                },
                "goal": {
                    "type": "string",
                    "description": "学习目标（可选）"
                }
            },
            "required": ["topic"]
        }
    }
}


def get_ai_powered_tools():
    """
    获取AI驱动的工具列表
    
    Returns:
        工具信息列表
    """
    return [
        {
            "name": "web_content_analyzer",
            "func": web_content_analyzer,
            "description": "智能网页内容分析器。抓取网页并进行深度分析，包括内容摘要、关键词提取、情感分析等。需要AI的理解和分析能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["web_content_analyzer"]["parameters"]
        },
        {
            "name": "text_quality_analyzer",
            "func": text_quality_analyzer,
            "description": "文本质量智能分析器。分析文本的语言表达、逻辑结构、语法错误，并提供专业的改进建议。需要AI的语言理解和评估能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["text_quality_analyzer"]["parameters"]
        },
        {
            "name": "creative_idea_generator",
            "func": creative_idea_generator,
            "description": "创意想法生成器。为特定主题生成创新性的想法，包括商业模式、产品功能、营销方案等。需要AI的创造力和发散思维。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["creative_idea_generator"]["parameters"]
        },
        {
            "name": "code_review_assistant",
            "func": code_review_assistant,
            "description": "代码智能审查助手。对代码进行专业审查，发现潜在问题、提供优化建议和改进方案。需要AI的代码理解和工程经验。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["code_review_assistant"]["parameters"]
        },
        {
            "name": "decision_analyzer",
            "func": decision_analyzer,
            "description": "决策智能分析器。分析决策场景，对比各个方案的优劣，提供理性的决策建议。需要AI的多维度分析和推理能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["decision_analyzer"]["parameters"]
        },
        {
            "name": "data_insight_generator",
            "func": data_insight_generator,
            "description": "数据洞察生成器。分析数据样本，发现规律和趋势，提供有价值的数据洞察。需要AI的数据理解和分析能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["data_insight_generator"]["parameters"]
        },
        {
            "name": "content_improver",
            "func": content_improver,
            "description": "内容智能优化器。优化文本内容的表达方式，提升内容质量。支持多种风格转换。需要AI的语言生成和改写能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["content_improver"]["parameters"]
        },
        {
            "name": "problem_solver",
            "func": problem_solver,
            "description": "智能问题解决器。分析复杂问题，提供系统性的解决方案和实施步骤。需要AI的问题分解和推理能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["problem_solver"]["parameters"]
        },
        {
            "name": "meeting_summarizer",
            "func": meeting_summarizer,
            "description": "会议智能总结器。将会议记录转换为结构化的会议总结，包括讨论要点、决策事项、待办任务等。需要AI的信息提取和结构化能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["meeting_summarizer"]["parameters"]
        },
        {
            "name": "learning_path_designer",
            "func": learning_path_designer,
            "description": "学习路径设计器。为特定主题设计系统的学习路径，包括知识体系、学习资源、实践建议等。需要AI的知识整合和规划能力。",
            "parameters": AI_POWERED_TOOL_DEFINITIONS["learning_path_designer"]["parameters"]
        }
    ]

