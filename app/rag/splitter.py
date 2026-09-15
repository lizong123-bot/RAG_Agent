from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_docs(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )

    return splitter.split_documents(docs)

if __name__ == "__main__":
    import  loader
    path = r"Y:\实验报告\实训\ai _agent\货币金融学+米什金（中文版第九版）.pdf"

    loader_docs = loader.load_document(path)


    chunks = split_docs(loader_docs)
    print(f"原始文档数: {len(loader_docs)}")
    print(f"切分后 chunk 数: {len(chunks)}")


