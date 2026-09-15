from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    EMBEDDING_API_KEY,
    EMBEDDING_MODEL_ID,
    EMBEDDING_BASE_URL,
)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL_ID,
        api_key=EMBEDDING_API_KEY,
        base_url=EMBEDDING_BASE_URL,
        check_embedding_ctx_length=False,
    )


def build_vectorstore(chunks: list[Document]) -> QdrantVectorStore:
    """把切分后的文档写入 Qdrant。集合不存在时自动创建。"""

    return QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=QDRANT_COLLECTION_NAME,
        batch_size=10,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )


def get_vectorstore() -> QdrantVectorStore:
    """只连接已有集合，用于检索。"""
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=QDRANT_COLLECTION_NAME,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )