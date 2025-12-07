"""Quick test of OpenRouter for multi-model support"""
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def test_openrouter():
    """Test OpenRouter with different models"""
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    models = [
        "openai/gpt-4o-mini",
        "google/gemini-2.0-flash-exp",
        "x-ai/grok-beta", 
        "deepseek/deepseek-chat"
    ]
    
    for model in models:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"Say '{model.split('/')[0]} works!'"}],
                max_tokens=10
            )
            print(f"✅ {model}: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ {model}: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
