"""
模型配置验证脚本

用于验证模型配置是否正确加载
"""

from shuyixiao_agent.config import settings


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def validate_config():
    """验证配置"""
    print("\n🔍 正在验证模型配置...")
    
    # 基础配置
    print_section("基础配置")
    print(f"API Base URL: {settings.gitee_ai_base_url}")
    print(f"SSL Verify: {settings.ssl_verify}")
    
    api_key = settings.gitee_ai_api_key
    if api_key:
        print(f"API Key: {api_key[:10]}...{api_key[-4:]} (已配置)")
    else:
        print("⚠️  API Key: 未配置！请在 .env 文件中设置 GITEE_AI_API_KEY")
        return False
    
    # 主对话模型配置
    print_section("主对话模型配置")
    print(f"使用云端模型: {settings.use_cloud_chat_model}")
    print(f"主对话模型: {settings.gitee_ai_model}")
    if not settings.use_cloud_chat_model:
        print(f"本地模型路径: {settings.local_chat_model or '未配置'}")
        print(f"本地模型设备: {settings.local_chat_device}")
    
    # Agent 模型配置
    print_section("Agent 模型配置")
    if settings.agent_model:
        print(f"Agent 专用模型: {settings.agent_model}")
    else:
        print(f"Agent 使用主对话模型: {settings.gitee_ai_model}")
    print(f"最大迭代次数: {settings.agent_max_iterations}")
    print(f"故障转移: {settings.enable_failover}")
    
    # 查询优化模型配置
    print_section("查询优化模型配置")
    if settings.query_optimizer_model:
        print(f"查询优化专用模型: {settings.query_optimizer_model}")
    else:
        print(f"查询优化使用主对话模型: {settings.gitee_ai_model}")
    print(f"启用查询重写: {settings.enable_query_rewrite}")
    print(f"启用子查询扩展: {settings.enable_subquery_expansion}")
    
    # RAG 嵌入模型配置
    print_section("RAG 嵌入模型配置")
    if settings.use_cloud_embedding:
        print(f"使用云端嵌入服务: ✓")
        print(f"云端嵌入模型: {settings.cloud_embedding_model}")
    else:
        print(f"使用本地嵌入模型: ✓")
        print(f"本地嵌入模型: {settings.embedding_model}")
        print(f"设备: {settings.embedding_device}")
    
    # RAG 重排序模型配置
    print_section("RAG 重排序模型配置")
    if settings.use_cloud_reranker:
        print(f"使用云端重排序服务: ✓")
        print(f"云端重排序模型: {settings.cloud_reranker_model}")
    else:
        print(f"使用本地重排序模型: ✓")
        print(f"本地重排序模型: {settings.reranker_model}")
        print(f"设备: {settings.reranker_device}")
    
    # RAG 检索配置
    print_section("RAG 检索配置")
    print(f"向量数据库路径: {settings.vector_db_path}")
    print(f"文档分片大小: {settings.chunk_size}")
    print(f"分片重叠: {settings.chunk_overlap}")
    print(f"检索 Top K: {settings.retrieval_top_k}")
    print(f"重排序 Top K: {settings.rerank_top_k}")
    
    # 高级配置
    print_section("高级配置")
    print(f"最大上下文 Token: {settings.max_context_tokens}")
    print(f"启用上下文扩展: {settings.enable_context_expansion}")
    print(f"最大子查询数: {settings.max_subqueries}")
    print(f"请求超时时间: {settings.request_timeout}秒")
    print(f"最大重试次数: {settings.max_retries}")
    
    print("\n" + "=" * 60)
    print("✅ 配置验证完成！")
    print("=" * 60)
    
    return True


def test_model_connection():
    """测试模型连接"""
    print("\n🔗 正在测试模型连接...")
    
    try:
        from shuyixiao_agent.gitee_ai_client import GiteeAIClient
        
        client = GiteeAIClient()
        print(f"✓ 客户端初始化成功")
        print(f"✓ 使用模型: {client.model}")
        
        # 简单测试
        print("\n发送测试消息: '你好'")
        response = client.simple_chat("你好")
        print(f"✓ 模型响应: {response[:100]}...")
        
        print("\n✅ 模型连接测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 模型连接测试失败: {e}")
        print("\n可能的原因：")
        print("1. API Key 未配置或无效")
        print("2. 网络连接问题")
        print("3. 模型名称不正确")
        print("4. SSL 证书问题（尝试设置 SSL_VERIFY=false）")
        return False


def print_usage_tips():
    """打印使用提示"""
    print("\n" + "=" * 60)
    print("  使用提示")
    print("=" * 60)
    print("\n1. 查看所有可用模型：")
    print("   访问 https://ai.gitee.com/docs/products/apis")
    print("\n2. 修改模型配置：")
    print("   编辑项目根目录的 .env 文件")
    print("\n3. 配置不同任务使用不同模型：")
    print("   GITEE_AI_MODEL=DeepSeek-V3          # 主对话模型")
    print("   AGENT_MODEL=GLM-4-Flash             # Agent 专用模型（可选）")
    print("   QUERY_OPTIMIZER_MODEL=Qwen2.5-14B   # 查询优化模型（可选）")
    print("\n4. 查看详细配置文档：")
    print("   docs/model_configuration.md")
    print("\n5. 启用/禁用云端服务：")
    print("   USE_CLOUD_EMBEDDING=true            # 云端嵌入服务")
    print("   USE_CLOUD_RERANKER=true             # 云端重排序服务")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("    模型配置验证工具")
    print("🚀 " * 20)
    
    # 验证配置
    config_valid = validate_config()
    
    if not config_valid:
        print("\n❌ 配置验证失败，请检查 .env 文件配置")
        print_usage_tips()
        exit(1)
    
    # 测试连接
    print("\n是否测试模型连接？(y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y' or choice == 'yes':
            connection_ok = test_model_connection()
            if not connection_ok:
                print_usage_tips()
                exit(1)
    except KeyboardInterrupt:
        print("\n\n已取消测试")
    
    print_usage_tips()
    print("✅ 所有检查通过！现在可以开始使用了。\n")

