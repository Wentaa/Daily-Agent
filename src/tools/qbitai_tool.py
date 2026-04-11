"""抓取量子位RSS feed的最新文章"""

import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

QBITAI_RSS_URL = "https://www.qbitai.com/feed"
MAX_ITEMS = 20

TIME_RANGE_DAYS = {
    "today": 1,
    "7d": 7,
    "30d": 30,
}


def _parse_rss(xml_text: str, cutoff: datetime | None) -> List[Dict]:
    """解析RSS XML，提取文章列表，按cutoff过滤"""
    root = ET.fromstring(xml_text)
    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        description = item.findtext("description", "").strip()
        pub_date_str = item.findtext("pubDate", "").strip()

        if not title:
            continue

        # 按发布日期过滤
        if cutoff and pub_date_str:
            try:
                pub_date = parsedate_to_datetime(pub_date_str).replace(tzinfo=None)
                if pub_date < cutoff:
                    continue
            except (ValueError, TypeError):
                pass

        items.append({
            "title": title,
            "summary": description,
            "url": link,
            "source": "量子位",
        })

        if len(items) >= MAX_ITEMS:
            break

    return items


async def fetch_qbitai_news(time_range: str = "7d") -> List[Dict]:
    """通过RSS feed抓取量子位最新文章，按time_range过滤"""
    if time_range == "all":
        cutoff = None
    else:
        days = TIME_RANGE_DAYS.get(time_range, 7)
        cutoff = datetime.now() - timedelta(days=days)

    async with httpx.AsyncClient(
        timeout=30,
        headers={"User-Agent": "DailyAgent/1.0"},
        follow_redirects=True,
    ) as client:
        try:
            resp = await client.get(QBITAI_RSS_URL)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"[量子位] 抓取失败: {e}")
            return []

    return _parse_rss(resp.text, cutoff)
