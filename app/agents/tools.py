from langchain.tools import tool
from qdrant_client import models
from app.rag.retriever import get_retriever, format_docs_with_source

def _source_filter(name: str) -> models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.source",
                match=models.MatchValue(value=name),
            )
        ]
    )

@tool
def search_knowledge_base(query: str) -> str:
    """当问题涉及已上传文档的内容时，使用此工具检索私有知识库。
    适用于：询问文档里的具体事实、条款、定义、数据等。"""
    retriever = get_retriever(k=4)
    docs = retriever.invoke(query)
    return format_docs_with_source(docs)


@tool
def summarize_document(doc_name: str) -> str:
    """对指定文档生成摘要。输入为文件名，例如 'report.pdf'。"""
    from app.rag.vectorstore import get_vectorstore
    vs = get_vectorstore()
    docs = vs.similarity_search(
        query="summary",
        k=20,
        filter=_source_filter(doc_name),
    )
    if not docs:
        return f"未找到文档：{doc_name}"
    content = "\n".join(d.page_content for d in docs)
    return f"文档 {doc_name} 的主要内容片段：\n{content[:2000]}"


@tool
def compare_documents(doc_a: str) -> str:
    """对比两份文档的异同。请以 'docA|docB' 的形式传入两个文件名。"""
    if "|" not in doc_a:
        return "参数格式应为 '文件名A|文件名B'"
    a, b = [x.strip() for x in doc_a.split("|", 1)]

    from app.rag.vectorstore import get_vectorstore
    vs = get_vectorstore()

    docs_a = vs.similarity_search("key points", k=10, filter=_source_filter(a))
    docs_b = vs.similarity_search("key points", k=10, filter=_source_filter(b))

    if not docs_a or not docs_b:
        return f"未找到文档：{a if not docs_a else b}"

    text_a = "\n".join(d.page_content for d in docs_a)[:1500]
    text_b = "\n".join(d.page_content for d in docs_b)[:1500]
    return (
        f"=== {a} 摘要片段 ===\n{text_a}\n\n"
        f"=== {b} 摘要片段 ===\n{text_b}\n\n"
        f"请基于以上内容对比两份文档的异同。"
    )


ALL_TOOLS = [search_knowledge_base, summarize_document, compare_documents]

if __name__ == '__main__':
    from app.rag.vectorstore import get_vectorstore
    vs = get_vectorstore()
    hits = vs.similarity_search("测试", k=1)
    print(hits[0].metadata)
    # 1. 测试检索工具
    print("=== search_knowledge_base ===")
    print(search_knowledge_base.invoke("货币的定义是什么？"))

    # 2. 测试摘要工具（先确认向量库里有这个文件名）
    print("\n=== summarize_document ===")
    print(summarize_document.invoke("货币金融学+米什金（中文版第九版）.pdf"))

    # 3. 测试对比工具（用 | 分隔两个文件名）
    print("\n=== compare_documents ===")
    print(compare_documents.invoke("第9章 集成学习.pdf|货币金融学+米什金（中文版第九版）.pdf"))

