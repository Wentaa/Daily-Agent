"""MCP Server：将每日AI简报Agent暴露为MCP工具"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.agents.briefing_agent import build_graph

load_dotenv()

mcp = FastMCP("daily-agent-news")


@mcp.tool()
async def get_daily_agent_news(
    language: str = "zh",
    time_range: str = "7d",
    categories: list[str] | None = None,
) -> str:
    """获取每日AI情报简报，聚合GitHub Trending、HuggingFace Papers、量子位等数据源，经LLM筛选摘要后返回结构化简报。

    Args:
        language: 语言，"zh"中文 或 "en"英文，默认"zh"
        time_range: 时间范围，"today"今天 / "7d"近7天 / "30d"近30天，默认"7d"
        categories: 内容类型列表，可选值：开源项目、论文、模型发布、产品动态（英文时用Open Source/Papers/Model Release/Product News），默认全选
    """
    if categories is None:
        if language == "en":
            categories = ["Open Source", "Papers", "Model Release", "Product News"]
        else:
            categories = ["开源项目", "论文", "模型发布", "产品动态"]

    graph = build_graph()
    result = await graph.ainvoke({
        "raw_items": [],
        "filtered_items": [],
        "final_items": [],
        "status": "",
        "time_range": time_range,
        "language": language,
        "categories": categories,
    })

    # 格式化输出
    items = result.get("final_items", [])
    if not items:
        return "未找到相关AI简报内容。" if language == "zh" else "No relevant AI briefing found."

    lines = []
    for i, item in enumerate(items, 1):
        lines.append(
            f"{i}. 【{item['category']}】{item['title']}\n"
            f"   摘要：{item['summary']}\n"
            f"   来源：{item['source']} | {item['url']}"
        )

    header = "📋 每日AI情报简报" if language == "zh" else "📋 Daily AI Briefing"
    return f"{header}\n{'=' * 40}\n\n" + "\n\n".join(lines)


if __name__ == "__main__":
    mcp.run()
