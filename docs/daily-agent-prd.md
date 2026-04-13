# Daily Agent PRD

<aside>
<img src="https://www.notion.so/icons/token_gray.svg" alt="https://www.notion.so/icons/token_gray.svg" width="40px" />

**Overview:** 这是一个面向 AI 产品经理的每日情报简报 Agent，自动聚合 GitHub Trending、Hugging Face Daily Papers 和量子位的最新动态，经过筛选、摘要、分类后生成一份结构化简报。每条内容提取关键信息并附上原文链接，由用户自行决定是否深入阅读。目标是让 AI PM 每天用 5 分钟完成情报获取，不再需要手动刷多个平台。

</aside>

### Goals

*What measurable outcomes define success for this tool, and how will we track progress toward them?*

- 每日信息搜集与筛选时间从 30 分钟缩短至 10 分钟以内
- 每日简报覆盖 GitHub Trending + Hugging Face Daily Papers，以及量子位输出不少于 15 条摘要，每条附原文链接

### Users

*Who will use this tool, and what do they need to accomplish their work effectively?*

| **Role** | **Primary Needs** |
| --- | --- |
| AI 产品经理（个人使用） | 每天选择当日关注的内容类型，获取与之相关的 GitHub、HuggingFace和量子位最新动态摘要，自行决定是否深读原文 |

### Problem

*What are the current pain points and inefficiencies that this tool needs to solve?*

AI 领域信息分散在 GitHub、Hugging Face、量子位等多个平台，AI PM 每天需要逐一手动浏览，筛选成本高、耗时长（约 30 分钟以上）。论文和项目介绍篇幅较长，难以快速判断与当前工作的相关性，导致要么花大量时间通读、要么错过重要内容。此外，不同平台信息格式不统一，缺乏按个人关注点过滤的机制。

### Scope

*What features and boundaries will this tool include, and what will remain out of scope?*

## **In Scope**

- GitHub Trending 自动抓取（过滤 AI 相关内容）
- Hugging Face Daily Papers 自动抓取
- 量子位 RSS 抓取（国内产品动态）
- 按用户选择的内容类型（多选）过滤相关内容
- 每条内容生成一句话摘要 + 附原文链接
- 网页端展示结构化简报
- 实时显示 Agent 工作流程图
- MCP Server支持，可在Claude Desktop或任意MCP兼容客户端中直接调用

## **Non-goals（不做）**

- 邮件 / 微信推送
- 用户账号系统
- 历史简报存档
- 多用户支持
- 第二个国内来源（机器之心 / ModelScope，MVP 后视需求迭代）
- MCP多工具编排（当前仅暴露单一工具接口）

### Key Flows

*What are the critical user journeys that will drive adoption and daily usage of this tool?*

- 打开网页
- 勾选今日关注的内容类型（多选）：开源项目/工具、最新研究/论文、模型发布、产品动态（国内）
- 点击「生成简报」
- 实时查看 Agent 工作流程图（抓取 → 过滤 → 摘要 → 输出各阶段）
- 阅读结构化简报，每条附原文链接，点击跳转原文

### Requirements

*What are the functional and technical requirements needed to deliver the core user flows?*

## **功能要求**

- 支持内容类型多选过滤
- 自动抓取 GitHub Trending、Hugging Face Daily Papers、量子位
- 每条内容输出：标题 + 一句话摘要 + 分类标签 + 原文链接
- 实时展示 Agent 各节点工作状态

## **技术要求**

- FastAPI 后端 + LangGraph 实现多节点 Agent 流程
- SSE 实时推送 Agent 状态到前端
- Streamlit 或轻量 HTML 前端

### Metrics

*What key performance indicators will help us measure whether this tool is delivering value and meeting its goals?*

- 每日信息搜集与筛选时间从 30 分钟缩短至 10 分钟以内
- 每日简报覆盖不少于 15 条内容，每条附摘要与原文链接

### Open Questions

*What critical decisions or clarifications are still needed before we can finalize the design and implementation?*

- 量子位以外是否加入第二个国内来源（机器之心 / ModelScope）？

[Launch Checklist](./launch-checklist.csv)