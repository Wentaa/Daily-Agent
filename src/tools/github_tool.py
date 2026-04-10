"""抓取GitHub上AI相关的热门项目（通过GitHub Search API）"""

import httpx
from typing import List, Dict
from datetime import datetime, timedelta

GITHUB_API_BASE = "https://api.github.com"

# time_range到天数的映射
TIME_RANGE_DAYS = {
    "today": 1,
    "7d": 7,
    "30d": 30,
}


async def fetch_github_trending(time_range: str = "7d") -> List[Dict]:
    """通过GitHub Search API抓取近期AI相关热门项目，返回star数最高的20条"""
    keywords = 'llm OR langchain OR "ai agent" OR "mcp server" OR RAG OR langgraph'

    if time_range == "all":
        q = keywords
    else:
        days = TIME_RANGE_DAYS.get(time_range, 7)
        created_after = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        q = f"{keywords} created:>{created_after}"

    url = f"{GITHUB_API_BASE}/search/repositories?q={q}&sort=stars&order=desc&per_page=20"

    async with httpx.AsyncClient(
        timeout=30,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DailyAgent/1.0",
        },
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError:
            return []

    items = []
    for repo in resp.json().get("items", []):
        items.append({
            "title": repo["full_name"],
            "description": repo.get("description") or "",
            "url": repo["html_url"],
            "stars": str(repo.get("stargazers_count", 0)),
            "source": "GitHub",
        })

    return items
