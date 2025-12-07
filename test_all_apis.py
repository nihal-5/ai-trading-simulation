"""Test all APIs with new Gemini key"""
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def test_all():
    from openai import AsyncOpenAI
    import requests
    
    results = {}
    
    # 1. OpenAI (via OpenRouter)
    try:
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        r = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        results["OpenAI GPT-4"] = "✅ " + r.choices[0].message.content
    except Exception as e:
        results["OpenAI GPT-4"] = f"❌ {e}"
    
    # 2. Gemini (direct API)
    try:
        client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key="AIzaSyCstHSIEexlAtS0DoJUEWYkXa4sQI7qkac"
        )
        r = await client.chat.completions.create(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        results["Gemini"] = "✅ " + r.choices[0].message.content
    except Exception as e:
        results["Gemini"] = f"❌ {e}"
    
    # 3. Deepseek (via OpenRouter)
    try:
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        r = await client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        results["Deepseek"] = "✅ " + r.choices[0].message.content
    except Exception as e:
        results["Deepseek"] = f"❌ {e}"
    
    # 4. Polygon
    try:
        api_key = os.getenv("POLYGON_API_KEY")
        url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("results"):
            price = data["results"][0]["c"]
            results["Polygon"] = f"✅ AAPL ${price}"
        else:
            results["Polygon"] = f"❌ {data}"
    except Exception as e:
        results["Polygon"] = f"❌ {e}"
    
    # 5. Brave Search
    try:
        api_key = os.getenv("BRAVE_API_KEY")
        headers = {"X-Subscription-Token": api_key}
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params={"q": "test"},
            timeout=10
        )
        data = response.json()
        if data.get("web"):
            results["Brave Search"] = f"✅ {len(data['web'].get('results', []))} results"
        else:
            results["Brave Search"] = f"❌ {data}"
    except Exception as e:
        results["Brave Search"] = f"❌ {e}"
    
    return results

async def main():
    print("🧪 Testing All APIs...\n")
    results = await test_all()
    
    for name, status in results.items():
        print(f"{name:20} {status}")
    
    working = sum(1 for r in results.values() if "✅" in r)
    print(f"\n�� {working}/{len(results)} APIs Working")

if __name__ == "__main__":
    asyncio.run(main())
