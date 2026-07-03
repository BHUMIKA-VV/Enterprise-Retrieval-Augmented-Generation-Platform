import os
import pandas as pd

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader
)

from app.rag.embedding import EmbeddingModel
from app.rag.milvus_client import milvus_client


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)


# =====================================================
# EXCEL PARSER (NEW)
# =====================================================
def parse_excel(file_path: str):

    df = pd.read_excel(file_path)

    rows = []

    for i, row in df.iterrows():

        item = {}

        for col in df.columns:
            item[col] = "" if pd.isna(row[col]) else str(row[col])

        rows.append(item)

    return rows


# =====================================================
# LOAD NORMAL FILES
# =====================================================
def load_documents(file_path: str):

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)

    elif ext == ".docx":
        loader = UnstructuredWordDocumentLoader(file_path)

    elif ext in [".txt", ".md"]:
        loader = TextLoader(
            file_path=file_path,
            encoding="utf-8",
            autodetect_encoding=True
        )

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return loader.load()


# =====================================================
# MAIN INGEST (FINAL VERSION)
# =====================================================
def ingest_file(file_path: str, kb_name: str = "default"):

    ext = os.path.splitext(file_path)[1].lower()

    vectors = []
    payloads = []

    # =====================================================
    # 1. EXCEL RULE FILE (NEW LOGIC)
    # =====================================================
    if ext in [".xlsx", ".xls"]:

        rows = parse_excel(file_path)

        if not rows:
            raise ValueError("Empty Excel file")

        texts = []

        for i, row in enumerate(rows):

            # 👉 自动适配列名（你可以按自己Excel调整）
            material = row.get("材料名称") or row.get("material") or ""
            requirement = row.get("要求") or row.get("requirement") or ""

            text = f"""
材料名称：{material}
要求：{requirement}
""".strip()

            texts.append(text)

            embedding = EmbeddingModel.embed_query(text)

            vectors.append(embedding)

            payloads.append({
                "text": text,
                "source": os.path.basename(file_path),
                "kb_name": kb_name,
                "type": "excel_rule",
                "row_id": i,
                "material": material
            })

    # =====================================================
    # 2. NORMAL FILES (PDF / DOCX / TXT)
    # =====================================================
    else:

        documents = load_documents(file_path)

        chunks = text_splitter.split_documents(documents)

        texts = [
            doc.page_content
            for doc in chunks
            if doc.page_content.strip()
        ]

        if not texts:
            raise ValueError("No valid text extracted from document")

        embeddings = EmbeddingModel.embed_documents(texts)

        for doc, embedding in zip(chunks, embeddings):

            vectors.append(embedding)

            payloads.append({
                "text": doc.page_content,
                "source": os.path.basename(file_path),
                "kb_name": kb_name,
                "type": "document"
            })

    # =====================================================
    # 3. INSERT INTO MILVUS
    # =====================================================
    milvus_client.insert(
        vectors=vectors,
        payloads=payloads
    )

    return {
        "success": True,
        "chunks": len(vectors),
        "filename": os.path.basename(file_path),
        "type": "excel" if ext in [".xlsx", ".xls"] else "document"
    }