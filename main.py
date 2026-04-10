"""FastAPI入口，SSE推送"""

import json
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src.agents.briefing_agent import build_graph

load_dotenv()

app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")


class GenerateRequest(BaseModel):
    categories: List[str]
    time_range: str = "7d"


@app.get("/")
async def index():
    """返回前端页面"""
    return FileResponse("static/index.html")


# 节点名称映射：LangGraph内部节点名 → SSE推送的节点名
NODE_MAP = {
    "fetch": "fetch",
    "filter": "filter",
    "summarize": "summarize",
    "output": "output",
}

# 各节点对应的数量字段
NODE_COUNT_KEY = {
    "fetch": "raw_items",
    "filter": "filtered_items",
    "summarize": "final_items",
    "output": "final_items",
}


@app.post("/generate")
async def generate(req: GenerateRequest):
    """启动briefing_agent，通过SSE实时推送节点状态"""

    async def event_stream():
        graph = build_graph()
        initial_state = {
            "raw_items": [],
            "filtered_items": [],
            "final_items": [],
            "status": "",
            "time_range": req.time_range,
        }

        final_items = []

        # 先推送所有节点的pending状态
        for node in ["fetch", "filter", "summarize", "output"]:
            yield json.dumps(
                {"node": node, "status": "pending", "count": 0},
                ensure_ascii=False,
            )

        # astream逐节点yield状态更新，只推done
        async for event in graph.astream(initial_state):
            for node_name, state_update in event.items():
                sse_node = NODE_MAP.get(node_name, node_name)
                count_key = NODE_COUNT_KEY.get(node_name)
                count = len(state_update.get(count_key, [])) if count_key else 0

                yield json.dumps(
                    {"node": sse_node, "status": "done", "count": count},
                    ensure_ascii=False,
                )

                if "final_items" in state_update:
                    final_items.clear()
                    final_items.extend(state_update["final_items"])

        # 推送最终完成事件
        yield json.dumps(
            {"node": "complete", "final_items": final_items},
            ensure_ascii=False,
        )

    return EventSourceResponse(event_stream())
