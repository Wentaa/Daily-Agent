"""prompt管理"""

FILTER_PROMPT = """\
你是一个AI领域内容筛选助手。判断以下内容是否与AI应用、Agent、LLM、大模型、机器学习相关，并给出分类。

## 输入
标题：{title}
摘要：{summary}

## 判断标准
- 相关：涉及LLM应用开发、AI Agent、RAG、多模态应用、AI产品发布、开源AI工具/框架、模型能力评测、Prompt工程
- 不相关：纯图像生成/视频生成/语音合成（无应用价值）、机器人控制、点云处理、医学影像、纯数学/物理研究、与AI产品开发无直接关联的基础研究

## 分类标签（仅在relevant为true时需要）
- 开源项目：GitHub上的开源工具、框架、库
- 论文：学术论文、技术报告、研究成果
- 模型发布：新模型发布、模型更新、benchmark结果
- 产品动态：商业产品发布、功能更新、行业新闻

## 输出要求
只输出JSON，不要输出其他内容：
{{"relevant": true/false, "category": "从以下四个选项中选一个：开源项目、论文、模型发布、产品动态", "reason": "简短理由"}}
"""

SUMMARIZE_PROMPT = """\
你是一个面向AI产品经理的简报编辑。将以下内容压缩成一句话中文摘要。

## 输入
标题：{title}
摘要：{summary}
来源：{source}

## 输出要求
只输出JSON，不要输出其他内容：
{{"summary": "一句话中文摘要，不超过80字"}}
"""

FILTER_PROMPT_EN = """\
You are an AI content screening assistant. Determine whether the following content is related to AI applications, Agents, LLMs, or machine learning, and assign a category.

## Input
Title: {title}
Summary: {summary}

## Criteria
- Relevant: LLM application development, AI Agent, RAG, multimodal applications, AI product launches, open-source AI tools/frameworks, model benchmarking, prompt engineering
- Not relevant: pure image/video generation or speech synthesis (without application value), robot control, point cloud processing, medical imaging, pure math/physics research, foundational research not directly related to AI product development

## Categories (only needed when relevant is true)
- Open Source: open-source tools, frameworks, and libraries on GitHub
- Paper: academic papers, technical reports, research findings
- Model Release: new model releases, model updates, benchmark results
- Product Update: commercial product launches, feature updates, industry news

## Output
Output JSON only, nothing else:
{{"relevant": true/false, "category": "choose one from: Open Source, Paper, Model Release, Product Update", "reason": "brief reason"}}
"""

SUMMARIZE_PROMPT_EN = """\
You are a briefing editor for AI product managers. Compress the following content into a one-sentence English summary.

## Input
Title: {title}
Summary: {summary}
Source: {source}

## Output
Output JSON only, nothing else:
{{"summary": "one-sentence English summary, no more than 80 words"}}
"""
