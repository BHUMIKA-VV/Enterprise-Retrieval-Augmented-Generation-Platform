from app.rag.embedding import EmbeddingModel
from app.rag.milvus_client import milvus_client
import uuid

docs = [
    "Milvus is a vector database for similarity search.",
    "RAG combines retrieval and generation using LLMs.",
    "BGE is a strong embedding model from BAAI.",
    "LangChain is a framework for building LLM applications.Test"
]


# =========================
# 清空 default（只用 client）
# =========================
def clear_default():

    try:
        print("🧹 Clearing default KB...")

        # ⚠️ 前提：你的 client 必须支持 delete by filter
        milvus_client.delete(
            expr='kb_name == "default"'
        )

        print("✅ default cleared via milvus_client")

    except Exception as e:
        print("⚠️ clear failed:", e)
        print("👉 如果报错，说明 milvus_client 没有 delete 方法")


# =========================
# 写入
# =========================
def ingest():

    vectors = []
    payloads = []

    for doc in docs:

        vec = EmbeddingModel.embed_documents(doc)

        vectors.append(vec)

        payloads.append({
            "id": str(uuid.uuid4()),
            "text": doc,
            "kb_name": "default"
        })

    milvus_client.insert(
        vectors=vectors,
        payloads=payloads
    )

    print("✅ ingestion done")


if __name__ == "__main__":

    clear_default()
    #ingest()