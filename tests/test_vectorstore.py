from langchain_core.documents import Document


def test_qdrant_roundtrip():
    from app.rag.vectorstore import build_vectorstore

    docs = [
        Document(
            page_content="LangGraph 是一个用于构建有状态智能体的编排框架。",
            metadata={"source": "test.md", "page": 1},
        )
    ]
    vs = build_vectorstore(docs)
    results = vs.similarity_search("LangGraph 是什么", k=1)
    assert len(results) >= 1
    assert "LangGraph" in results[0].page_content