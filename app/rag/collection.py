from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from app.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME

VECTOR_SIZE = 1024


def get_client() -> QdrantClient:
    """创建 Qdrant 客户端；有 API Key 走 Cloud，否则走本地。"""
    if QDRANT_API_KEY:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(url=QDRANT_URL)


def ensure_collection(client: QdrantClient, vector_size: int = VECTOR_SIZE) -> None:
    """集合不存在则创建，避免首次写入报错。"""
    existing = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"✅ 已创建 collection: {QDRANT_COLLECTION_NAME}")
    else:
        print(f"ℹ️ collection 已存在: {QDRANT_COLLECTION_NAME}")


def ensure_source_index(client: QdrantClient) -> None:
    """给 metadata.source 建 keyword 索引（幂等）。"""
    client.create_payload_index(
        collection_name=QDRANT_COLLECTION_NAME,
        field_name="metadata.source",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    print("✅ metadata.source 索引已就绪")