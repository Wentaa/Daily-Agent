# CLAUDE.md

## 项目简介
每日AI情报简报Agent，面向AI产品经理，自动聚合GitHub Trending、
Hugging Face Daily Papers、量子位，经LLM筛选摘要后生成结构化简报。

## 技术栈
- Agent框架：LangGraph
- LLM：Anthropic Claude（claude-sonnet-4-6）
- 后端：FastAPI + SSE
- 数据抓取：httpx（异步）
- 前端：原生HTML + JS
- 部署：Railway

## 目录结构
daily-agent/
├── main.py              # FastAPI入口，SSE推送
├── CLAUDE.md            # 本文件
├── .env                 # 环境变量，不提交git
├── requirements.txt     # 依赖
├── static/
│   └── index.html       # 前端页面
└── src/
    ├── agents/
    │   └── briefing_agent.py   # LangGraph图定义
    ├── tools/
    │   ├── github_tool.py      # 抓GitHub Trending
    │   ├── huggingface_tool.py # 抓HuggingFace Papers
    │   └── qbitai_tool.py      # 抓量子位RSS
    └── prompts/
        └── prompts.py          # 所有prompt集中管理

## 数据流
用户选内容类型 → FastAPI接收 → LangGraph启动
→ fetch_node（httpx并行抓取）
→ filter_node（Claude过滤不相关内容）
→ summarize_node（Claude生成摘要+分类标签）
→ output_node（整理结构化JSON）
→ SSE实时推送每个节点状态到前端

## 每条简报输出格式
{
  "title": "标题",
  "summary": "一句话摘要",
  "category": "开源项目/论文/模型发布/产品动态",
  "url": "原文链接",
  "source": "GitHub/HuggingFace/量子位"
}

## 代码规范
- 所有异步函数用async/await
- 工具函数返回List[Dict]
- 环境变量统一从.env读取，用python-dotenv
- 不要在tool文件里调用LLM，LLM只在agent里调用
- 每个函数写简短注释说明用途

## 命名习惯
- 文件名：snake_case
- 函数名：snake_case
- 常量：UPPER_CASE
- prompt变量：FILTER_PROMPT、SUMMARIZE_PROMPT

## 注意事项
- .env不提交git，记得加.gitignore
- HuggingFace直连，国内环境如有问题换hf-mirror.com
- LLM调用只在filter_node和summarize_node里发生
- prompt统一在prompts.py里修改，不要散落在agent代码里