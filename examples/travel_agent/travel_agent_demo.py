"""
示例: 智能旅行助手 Agent

基于 Datawhale《Hello-Agents》教程 1.3 节 "动手体验：5 分钟实现第一个智能体"
演示 Thought-Action-Observation 循环模式，使用 Moark (Gitee AI) API

该示例展示了如何构建一个能处理分步任务的智能旅行助手：
1. 接收用户请求："查询今天北京的天气，然后根据天气推荐合适的旅游景点"
2. 调用天气查询工具获取实时天气
3. 基于天气情况调用景点推荐工具
4. 综合信息给出最终建议

运行前准备：
1. 确保 .env 文件中配置了 GITEE_AI_API_KEY
2. 或在运行配置中设置环境变量 GITEE_AI_API_KEY
"""

import sys
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from examples.travel_agent.weather_tools import get_weather, WEATHER_TOOL_DEFINITIONS
from examples.travel_agent.attraction_tools import get_attraction, ATTRACTION_TOOL_DEFINITIONS

# 加载环境变量
load_dotenv()

# ============================================
# Agent 系统提示词
# ============================================
AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气，包括温度、湿度、风速等。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点，会根据天气状况智能推荐室内或室外景点。

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对 Thought-Action:

Thought: [这里是你的思考过程和下一步计划]
Action: 你决定采取的行动，必须是以下格式之一:
- `function_name(arg_name="arg_value")`: 调用一个可用工具
- `Finish[最终答案]`: 当你认为已经获得最终答案时

当收集到足够的信息，能够回答用户的最终问题时，你必须在 Action: 字段后使用 Finish[最终答案] 来输出最终答案。

请开始吧！
"""


class TravelAgent:
    """
    智能旅行助手

    基于 Thought-Action-Observation 循环模式实现，
    能够处理需要多步骤推理和工具调用的复杂任务。
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化 Agent

        Args:
            api_key: Moark/Gitee AI API 密钥
            base_url: API 基础 URL
            model: 模型名称
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.available_tools = {
            "get_weather": get_weather,
            "get_attraction": get_attraction,
        }

    def generate(self, prompt: str, system_prompt: str) -> str:
        """
        调用 LLM API 生成回应

        Args:
            prompt: 用户提示
            system_prompt: 系统提示词

        Returns:
            LLM 的回复
        """
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            return answer
        except Exception as e:
            return f"错误: 调用语言模型服务时出错 - {e}"

    def parse_action(self, llm_output: str) -> tuple:
        """
        解析 LLM 输出中的 Thought 和 Action

        Args:
            llm_output: LLM 的原始输出

        Returns:
            (thought, action) 元组
        """
        # 解析 Thought
        thought_match = re.search(r'Thought:\s*(.*?)(?=\n\s*Action:|$)', llm_output, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""

        # 解析 Action
        action_match = re.search(r'Action:\s*(.*)', llm_output, re.DOTALL)
        action = action_match.group(1).strip() if action_match else ""

        return thought, action

    def execute_action(self, action_str: str) -> str:
        """
        执行 Action，调用相应的工具

        Args:
            action_str: Action 字符串

        Returns:
            工具执行结果（Observation）
        """
        if not action_str:
            return "错误: Action 字段为空"

        # 检查是否是 Finish
        if action_str.startswith("Finish"):
            final_answer_match = re.match(r'Finish\[(.*)\]', action_str)
            if final_answer_match:
                return f"FINISH:{final_answer_match.group(1)}"
            return "FINISH:"

        # 解析函数调用
        func_match = re.search(r'(\w+)\((.*)\)', action_str)
        if not func_match:
            return f"错误: 无法解析 Action 格式: {action_str}"

        func_name = func_match.group(1)
        args_str = func_match.group(2)

        # 解析参数
        kwargs = {}
        if args_str:
            kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        # 调用工具
        if func_name in self.available_tools:
            try:
                result = self.available_tools[func_name](**kwargs)
                return result
            except Exception as e:
                return f"错误: 调用工具 {func_name} 时出错 - {e}"
        else:
            return f"错误: 未定义的工具 '{func_name}'"

    def run(self, user_query: str, max_iterations: int = 5, verbose: bool = True) -> str:
        """
        运行 Agent 主循环

        Args:
            user_query: 用户查询
            max_iterations: 最大迭代次数
            verbose: 是否输出详细过程

        Returns:
            最终答案
        """
        if verbose:
            print("=" * 60)
            print("智能旅行助手")
            print("=" * 60)
            print(f"\n用户输入: {user_query}\n")

        # 初始化 prompt 历史
        prompt_history = [f"用户请求: {user_query}"]

        # 主循环
        for i in range(max_iterations):
            if verbose:
                print(f"--- 循环 {i + 1} ---\n")

            # 构建完整的 prompt
            full_prompt = "\n".join(prompt_history)

            # 调用 LLM 进行思考
            if verbose:
                print("正在调用大语言模型...")
            llm_output = self.generate(full_prompt, AGENT_SYSTEM_PROMPT)

            if verbose:
                print(f"模型输出:\n{llm_output}\n")

            # 解析 Thought 和 Action
            thought, action = self.parse_action(llm_output)

            # 将模型输出添加到历史
            prompt_history.append(llm_output)

            # 如果没有 Action，报错
            if not action:
                observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
                observation_str = f"Observation: {observation}"
                if verbose:
                    print(f"{observation_str}\n")
                prompt_history.append(observation_str)
                continue

            # 执行 Action
            observation = self.execute_action(action)

            # 检查是否完成
            if observation.startswith("FINISH:"):
                final_answer = observation.replace("FINISH:", "", 1)
                if verbose:
                    print(f"任务完成！\n")
                    print(f"最终答案: {final_answer}")
                return final_answer

            # 记录观察结果
            observation_str = f"Observation: {observation}"
            if verbose:
                print(f"{observation_str}\n")
                print("=" * 60 + "\n")
            prompt_history.append(observation_str)

        # 达到最大迭代次数
        return f"错误: 达到最大迭代次数 ({max_iterations})，未能完成任务"


def main():
    """主函数"""
    # 从环境变量读取配置
    api_key = os.getenv("GITEE_AI_API_KEY")
    base_url = os.getenv("GITEE_AI_BASE_URL", "https://api.moark.com/v1")
    model = os.getenv("GITEE_AI_MODEL", "DeepSeek-V3")

    if not api_key:
        print("错误: 请在 .env 文件中配置 GITEE_AI_API_KEY")
        print("或在运行配置中设置环境变量 GITEE_AI_API_KEY")
        return

    # 创建 Agent
    agent = TravelAgent(
        api_key=api_key,
        base_url=base_url,
        model=model
    )

    # 测试查询
    test_queries = [
        "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。",
        "上海今天天气怎么样？有没有适合去的景点？",
        "我想去成都旅游，那边天气如何？",
    ]

    for query in test_queries:
        result = agent.run(query, verbose=True)
        print("\n" + "=" * 60 + "\n")

    # 交互式模式
    print("=" * 60)
    print("进入交互模式（输入 'quit' 或 'exit' 退出）")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("你: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break

            if not user_input:
                continue

            result = agent.run(user_input, verbose=True)
            print()

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {str(e)}\n")


if __name__ == "__main__":
    main()
