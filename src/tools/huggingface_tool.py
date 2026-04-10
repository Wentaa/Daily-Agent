"""抓取Hugging Face Daily Papers的最新论文"""

import httpx
from typing import List, Dict
from datetime import datetime, timedelta

DAILY_PAPERS_API = "https://huggingface.co/api/daily_papers"

TIME_RANGE_DAYS = {
    "today": 1,
    "7d": 7,
    "30d": 30,
}


async def fetch_huggingface_papers(time_range: str = "7d") -> List[Dict]:
    """通过HuggingFace API抓取推荐论文列表，按time_range过滤发布日期"""
    async with httpx.AsyncClient(
        timeout=30,
        headers={"User-Agent": "DailyAgent/1.0"},
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(DAILY_PAPERS_API)
            resp.raise_for_status()
        except httpx.HTTPError:
            return []

    papers = resp.json()
    items = []

    # 计算截止日期
    if time_range == "all":
        cutoff = None
    else:
        days = TIME_RANGE_DAYS.get(time_range, 7)
        cutoff = datetime.now() - timedelta(days=days)

    for entry in papers:
        paper = entry.get("paper", {})
        paper_id = paper.get("id", "")
        title = paper.get("title", "")
        summary = paper.get("summary") or paper.get("ai_summary") or ""
        published_at = paper.get("publishedAt", "")

        if not title:
            continue

        # 按发布日期过滤
        if cutoff and published_at:
            try:
                pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00")).replace(tzinfo=None)
                if pub_date < cutoff:
                    continue
            except ValueError:
                pass

        items.append({
            "title": title,
            "summary": summary,
            "url": f"https://huggingface.co/papers/{paper_id}",
            "source": "HuggingFace",
        })

    return items[:10]
