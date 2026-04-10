"""LangGraph多节点Agent：抓取 → 过滤 → 摘要 → 输出"""

import asyncio
import json
import os
from typing import TypedDict, List, Dict

import anthropic
from langgraph.graph import StateGraph, END

from src.tools.github_tool import fetch_github_trending
from src.tools.huggingface_tool import fetch_huggingface_papers
from src.tools.qbitai_tool import fetch_qbitai_news
from src.prompts.prompts import FILTER_PROMPT, SUMMARIZE_PROMPT, FILTER_PROMPT_EN, SUMMARIZE_PROMPT_EN

MODEL = "claude-sonnet-4-6"


# ── State定义 ──────────────────────────────────────────────

class BriefingState(TypedDict):
    raw_items: List[Dict]
    filtered_items: List[Dict]
    final_items: List[Dict]
    status: str  # 当前节点状态，用于SSE推送
    time_range: str  # 时间范围：today/7d/30d/all
    language: str  # 语言：zh/en
    categories: List[str]  # 用户选择的内容类型


# ── LLM调用 ─────────────────────────────────────────────────

def _get_client() -> anthropic.AsyncAnthropic:
    """获取Anthropic异步客户端"""
    return anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def _call_llm(client: anthropic.AsyncAnthropic, prompt: str) -> str:
    """调用Claude，返回文本响应"""
    print(f"调用LLM，prompt长度：{len(prompt)}，内容前100字：{prompt[:100]}")
    message = await client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _parse_json(text: str) -> dict:
    """从LLM响应中解析JSON，兼容markdown代码块"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(text)


# ── 节点函数 ─────────────────────────────────────────────────

async def fetch_node(state: BriefingState) -> dict:
    """并行抓取三个数据源，合并结果"""
    time_range = state.get("time_range", "7d")
    github, huggingface, qbitai = await asyncio.gather(
        fetch_github_trending(time_range=time_range),
        fetch_huggingface_papers(time_range=time_range),
        fetch_qbitai_news(time_range=time_range),
    )

    # 统一字段：GitHub用description，其他用summary，统一成summary
    raw_items = []
    for item in github:
        raw_items.append({
            "title": item["title"],
            "summary": item.get("description") or item.get("summary", ""),
            "url": item["url"],
            "stars": item.get("stars", ""),
            "source": item["source"],
        })
    for item in huggingface + qbitai:
        raw_items.append({
            "title": item["title"],
            "summary": item.get("summary", ""),
            "url": item["url"],
            "source": item["source"],
        })

    return {"raw_items": raw_items, "status": "fetch_done"}


async def filter_node(state: BriefingState) -> dict:
    """用Claude逐条判断是否与AI相关，过滤不相关内容"""
    client = _get_client()
    filtered = []
    filter_prompt = FILTER_PROMPT_EN if state.get("language") == "en" else FILTER_PROMPT

    # 并发调用LLM进行过滤，限制并发数
    sem = asyncio.Semaphore(3)

    categories = state.get("categories", [])

    default_open_source = "Open Source" if state.get("language") == "en" else "开源项目"

    async def _check(item: Dict) -> Dict | None:
        # GitHub来源直接赋予"开源项目"category，跳过LLM
        if item.get("source") == "GitHub":
            if default_open_source not in categories:
                print(f"过滤：{item['title'][:30]} -> GitHub丢弃, 用户未选择{default_open_source}")
                return None
            print(f"过滤：{item['title'][:30]} -> GitHub直接保留, category={default_open_source}")
            return {**item, "category": default_open_source}
        async with sem:
            await asyncio.sleep(0.5)
            # 清洗文本，避免特殊字符导致API报错
            title = item["title"].replace("\n", " ").replace("\r", " ")[:100]
            summary = item["summary"].replace("\n", " ").replace("\r", " ")[:500]
            prompt = filter_prompt.format(title=title, summary=summary)
            try:
                result = _parse_json(await _call_llm(client, prompt))
                relevant = result.get("relevant")
                category = result.get("category", "")
                keep = relevant and category in categories
                print(f"过滤：{item['title'][:30]} -> relevant={relevant}, category={category}, {'保留' if keep else '丢弃'}")
                if not keep:
                    return None
                return {**item, "category": category}
            except (json.JSONDecodeError, KeyError) as e:
                print(f"过滤解析失败：{item['title']}，错误：{e}")
                return None

    tasks = [_check(item) for item in state["raw_items"]]
    results = await asyncio.gather(*tasks)
    filtered = [r for r in results if r is not None]

    return {"filtered_items": filtered, "status": "filter_done"}


async def summarize_node(state: BriefingState) -> dict:
    """用Claude为每条内容生成摘要"""
    client = _get_client()
    summarized = []
    summarize_prompt = SUMMARIZE_PROMPT_EN if state.get("language") == "en" else SUMMARIZE_PROMPT

    for item in state["filtered_items"]:
        prompt = summarize_prompt.format(
            title=item["title"],
            summary=item["summary"],
            source=item["source"],
        )
        try:
            result = _parse_json(await _call_llm(client, prompt))
            summarized.append({
                "title": item["title"],
                "summary": result.get("summary", item["summary"]),
                "category": item["category"],
                "url": item["url"],
                "source": item["source"],
            })
        except (json.JSONDecodeError, KeyError):
            summarized.append({
                "title": item["title"],
                "summary": item["summary"],
                "category": item["category"],
                "url": item["url"],
                "source": item["source"],
            })
        await asyncio.sleep(1)

    return {"final_items": summarized, "status": "summarize_done"}


async def output_node(state: BriefingState) -> dict:
    """整理最终输出"""
    return {"final_items": state["final_items"], "status": "output_done"}


# ── 构建LangGraph ───────────────────────────────────────────

def build_graph() -> StateGraph:
    """构建并返回编译后的LangGraph"""
    graph = StateGraph(BriefingState)

    graph.add_node("fetch", fetch_node)
    graph.add_node("filter", filter_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("output", output_node)

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "filter")
    graph.add_edge("filter", "summarize")
    graph.add_edge("summarize", "output")
    graph.add_edge("output", END)

    return graph.compile()
