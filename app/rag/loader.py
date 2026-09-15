import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document

def load_document(file_path: str) -> list[Document]:
    """支持 PDF / Markdown。"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in (".md", ".markdown"):
        loader = UnstructuredMarkdownLoader(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {ext}")

    docs = loader.load()
    for d in docs:
        d.metadata["source"] = os.path.basename(file_path)
    return docs