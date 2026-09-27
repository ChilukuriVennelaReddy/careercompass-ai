from groq import AsyncGroq
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def main():
    try:
        stream = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello in 10 words"}],
            max_tokens=100,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
        print("\nSuccess!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
