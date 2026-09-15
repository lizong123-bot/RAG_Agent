from collections import defaultdict

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from app.config import LLM_API_KEY, LLM_MODEL_ID, LLM_BASE_URL
from app.agents.tools import ALL_TOOLS


SYSTEM_PROMPT = (
    "你是一个严谨的知识库问答助手。\n"
    "规则：\n"
    "1. 如果问题涉及用户上传的私有文档内容，必须先调用 search_knowledge_base 工具，"
    "不要凭记忆回答。\n"
    "2. 如果是通用常识、闲聊或与文档无关的问题，直接回答，不要调用工具。\n"
    "3. 不要编造来源，来源必须来自工具的返回结果。\n"
    "4. 如果检索结果为空，如实告知用户“知识库中未找到相关内容”。\n"
    "5. 回答时请附上原文来源（文件名与页码）。"
)


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL_ID,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        temperature=0,
    )


def build_agent():
    return create_agent(
        model=get_llm(),
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )


_AGENT = None


def get_agent():
    global _AGENT
    if _AGENT is None:
        _AGENT = build_agent()
    return _AGENT


def extract_sources(messages) -> list[str]:
    sources = []
    for msg in messages:
        if msg.__class__.__name__ != "ToolMessage":
            continue
        content = str(getattr(msg, "content", ""))
        for line in content.splitlines():
            if line.startswith("[来源:"):
                src = line.strip("[]").replace("来源:", "").strip()
                if src not in sources:
                    sources.append(src)
    return sources


# ---------- 多轮对话（按 session 隔离）----------

_sessions: dict[str, list] = defaultdict(list)


def _trim_history(history: list, max_turns: int = 5) -> list:
    return history[-(max_turns * 2):]


def ask(question: str, session_id: str = "default") -> str:
    """按 session 隔离的多轮问答。"""
    agent = get_agent()
    history = _sessions[session_id]

    messages = history + [HumanMessage(content=question)]
    result = agent.invoke({"messages": messages})
    all_messages = result["messages"]

    answer = ""
    for m in reversed(all_messages):
        if m.__class__.__name__ == "AIMessage" and getattr(m, "content", ""):
            answer = m.content
            break
    if isinstance(answer, list):
        answer = "".join(b.get("text", "") for b in answer if isinstance(b, dict))
    if not answer:
        answer = "（Agent 未返回有效回答）"

    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=answer))
    _sessions[session_id] = _trim_history(history, max_turns=5)

    return answer


def reset_history(session_id: str = "default"):
    _sessions.pop(session_id, None)