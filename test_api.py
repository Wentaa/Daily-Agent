"""分步验证Anthropic API连接"""

import os
import asyncio
from dotenv import load_dotenv
import anthropic

load_dotenv()

# 1. 确认key加载正确
api_key = os.getenv("ANTHROPIC_API_KEY") or ""
print(f"[Step 1] API Key前10字符：{api_key[:10]}...")
if not api_key:
    print("错误：ANTHROPIC_API_KEY未设置")
    exit(1)

# 2. 发送测试消息
print("[Step 2] 发送测试消息...")
client = anthropic.Anthropic(api_key=api_key)
try:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=64,
        messages=[{"role": "user", "content": "hello"}],
    )
    print(f"成功！模型回复：{message.content[0].text}")
except anthropic.APIError as e:
    # 3. 打印完整错误信息
    print(f"[Step 3] API错误：{e}")
    print(f"状态码：{e.status_code}")
    print(f"响应headers：{dict(e.response.headers) if e.response else 'N/A'}")
    print(f"响应body：{e.body}")
except Exception as e:
    print(f"未知错误：{type(e).__name__}: {e}")

# 4. 异步调用测试
print("\n[Step 4] 测试异步调用...")

async def test_async():
    async_client = anthropic.AsyncAnthropic(api_key=api_key)
    try:
        message = await async_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=64,
            messages=[{"role": "user", "content": "hello"}],
        )
        print(f"异步调用成功！模型回复：{message.content[0].text}")
    except anthropic.APIError as e:
        print(f"异步调用API错误：{e}")
        print(f"状态码：{e.status_code}")
        print(f"响应headers：{dict(e.response.headers) if e.response else 'N/A'}")
    except Exception as e:
        print(f"异步调用未知错误：{type(e).__name__}: {e}")

asyncio.run(test_async())
