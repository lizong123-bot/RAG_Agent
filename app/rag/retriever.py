from langchain_core.retrievers import BaseRetriever
from app.rag.vectorstore import get_vectorstore
from app.utils.context_compress import compress_docs


def get_retriever(k: int = 4) -> BaseRetriever:
    vs = get_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})


def format_docs_with_source(docs,max_tokens: int = 2000) -> str:
    """把检索结果格式化成带来源引用的文本。"""
    if not docs:
        return "知识库中未找到相关内容。"
    docs = compress_docs(docs, max_tokens=max_tokens)
    parts = []
    for d in docs:
        source = d.metadata.get("source", "未知文件")
        page = d.metadata.get("page", "?")
        parts.append(f"[来源: {source} 第{page}页]\n{d.page_content}")
    return "\n\n".join(parts)