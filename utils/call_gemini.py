"""
Gemini API 调用工具
使用官方 Google Generative AI SDK
"""
import os
from google import genai

# 在初始化之前设置代理
# 如果需要使用代理，取消下面的注释并修改端口
# os.environ['http_proxy'] = 'http://127.0.0.1:15236'
# os.environ['https_proxy'] = 'http://127.0.0.1:15236'

def call_gemini(prompt: str, temperature: float = 1.0, model: str = "gemini-2.5-pro", stream: bool = True) -> str:
    """
    调用 Google Gemini API 生成内容（支持流式输出）

    Args:
        prompt: 提示词
        temperature: 温度参数，控制创造性 (0.0-2.0)
        model: 模型名称
        stream: 是否使用流式输出

    Returns:
        生成的文本内容
    """
    # 检测代理设置
    proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    print(f"🌐 当前代理: {proxy if proxy else '未设置'}")

    if not proxy:
        # 默认代理 - 请根据你的实际代理端口修改
        default_proxy = 'http://127.0.0.1:15236'  # 常见的代理端口
        print(f"⚠️  尝试使用默认代理: {default_proxy}")
        print(f"   如果失败，请检查代理软件是否运行，或修改此端口")
        os.environ['http_proxy'] = default_proxy
        os.environ['https_proxy'] = default_proxy

    # 获取 API Key
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 环境变量未设置")

    print(f"✓ API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        client = genai.Client(api_key=api_key)

        if stream:
            # 流式输出
            print("📡 开始流式生成...")
            full_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config={"temperature": temperature}
            ):
                text = chunk.text
                print(text, end='', flush=True)
                full_text += text
            print("\n✓ 生成完成")
            return full_text
        else:
            # 普通输出
            print("📡 开始生成...")
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"temperature": temperature}
            )
            print("✓ 生成完成")
            return response.text

    except Exception as e:
        print(f"\n✗ Gemini API 调用失败")
        print(f"   错误: {e}")
        print(f"   类型: {type(e).__name__}")
        print("\n💡 可能的解决方案:")
        print("   1. 检查代理软件是否运行（如 Clash、V2Ray）")
        print("   2. 确认代理端口是否正确（常见: 7890, 7891, 1080, 15236）")
        print("   3. 尝试直接访问 https://generativelanguage.googleapis.com")
        raise


if __name__ == "__main__":
    # 测试代码
    test_prompt = "写一个 100 字的科幻小说开头"

    print("调用 Gemini API...:")
    response = call_gemini(test_prompt, temperature=1.2)
    print(f"响应: {response}")
