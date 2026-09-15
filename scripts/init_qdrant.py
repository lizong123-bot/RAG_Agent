# scripts/init_qdrant.py
from app.rag.collection import get_client, ensure_collection, ensure_source_index

if __name__ == "__main__":
    client = get_client()
    ensure_collection(client)
    ensure_source_index(client)
    print("✅ Qdrant 初始化完成")