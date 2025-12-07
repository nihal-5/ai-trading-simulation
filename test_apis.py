"""Test all API keys to verify they work before building the system"""
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def test_openai():
    """Test OpenAI API"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OpenAI works!'"}],
            max_tokens=10
        )
        print(f"✅ OpenAI: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return False

async def test_gemini():
    """Test Google Gemini API"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        response = await client.chat.completions.create(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Say 'Gemini works!'"}],
            max_tokens=10
        )
        print(f"✅ Gemini: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        return False

async def test_grok():
    """Test Grok API"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url="https://api.x.ai/v1",
            api_key=os.getenv("GROK_API_KEY")
        )
        response = await client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": "Say 'Grok works!'"}],
            max_tokens=10
        )
        print(f"✅ Grok: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Grok failed: {e}")
        return False

async def test_deepseek():
    """Test Deepseek API"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Say 'Deepseek works!'"}],
            max_tokens=10
        )
        print(f"✅ Deepseek: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Deepseek failed: {e}")
        return False

async def test_polygon():
    """Test Polygon.io API"""
    try:
        import requests
        api_key = os.getenv("POLYGON_API_KEY")
        url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("results"):
            price = data["results"][0]["c"]
            print(f"✅ Polygon: AAPL price ${price}")
            return True
        else:
            print(f"❌ Polygon failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Polygon failed: {e}")
        return False

async def test_brave():
    """Test Brave Search API"""
    try:
        import requests
        api_key = os.getenv("BRAVE_API_KEY")
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"X-Subscription-Token": api_key}
        params = {"q": "test"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if data.get("web"):
            print(f"✅ Brave Search: Found {len(data['web'].get('results', []))} results")
            return True
        else:
            print(f"❌ Brave failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Brave failed: {e}")
        return False

async def main():
    print("🧪 Testing all API keys...\n")
    
    results = await asyncio.gather(
        test_openai(),
        test_gemini(),
        test_grok(),
        test_deepseek(),
        test_polygon(),
        test_brave(),
        return_exceptions=True
    )
    
    print(f"\n📊 Results: {sum(1 for r in results if r is True)}/6 APIs working")
    
if __name__ == "__main__":
    asyncio.run(main())
