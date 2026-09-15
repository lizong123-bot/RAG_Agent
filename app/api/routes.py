import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from qdrant_client import models

from app.config import DATA_DIR, QDRANT_COLLECTION_NAME
from app.rag.loader import load_document
from app.rag.splitter import split_docs
from app.rag.vectorstore import build_vectorstore
from app.rag.collection import get_client
from app.agents.react_agent import get_agent, extract_sources, ask as agent_ask, reset_history
from app.utils.token_counter import count_tokens

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    tokens_used: int


@router.post("/upload")
def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    save_path = os.path.join(DATA_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # 删掉同名旧数据，避免重复
        client = get_client()
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=models.Filter(
                must=[models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchValue(value=file.filename),
                )]
            ),
        )

        docs = load_document(save_path)
        chunks = split_docs(docs)
        build_vectorstore(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {e}")

    return {"message": "上传并入库成功", "file": file.filename, "chunks": len(chunks)}


@router.post("/ask", response_model=QueryResponse)
def ask(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        answer = agent_ask(req.question, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {e}")

    # 拿真 token 统计（简化：这里仍用估算）
    tokens = count_tokens(req.question) + count_tokens(answer)

    return QueryResponse(answer=answer, sources=[], tokens_used=tokens)