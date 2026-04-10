"""测试GitHub抓取"""

import asyncio
from src.tools.github_tool import fetch_github_trending

async def main():
    items = await fetch_github_trending()
    print(f"共抓取 {len(items)} 条")
    for item in items[:3]:
        print(f"  - {item['title']} (stars: {item['stars']})")

asyncio.run(main())
