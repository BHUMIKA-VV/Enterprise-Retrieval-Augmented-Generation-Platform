from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.chains.rag_chain import RAGChain
from app.chains.audit_chain import AuditChain
from app.router.query_router import route_intent_llm
import traceback
import os

router = APIRouter()

rag_chain = RAGChain()
audit_chain = AuditChain(rag_chain=rag_chain, llm=rag_chain.llm)


# =====================================================
# ⭐ 统一 attachments -> documents（关键新增）
# =====================================================
def normalize_attachments(attachments):
    """
    将多文件附件统一成标准 document 结构
    """

    if not attachments:
        return []

    documents = []

    for a in attachments:

        file_path = a.get("file_path")
        file_name = a.get("file_name")

        if not file_path:
            continue

        documents.append({
            "file_name": file_name,
            "file_path": file_path,
            "content": None  # 后续在 audit_chain / rag_chain 里再解析
        })

    return documents


# =====================================================
# CHAT API
# =====================================================
@router.post("/")
def chat(req: ChatRequest):

    print("======收到请求======")
    print(req)

    try:

        # =========================
        # 0. normalize attachments（关键）
        # =========================
        documents = normalize_attachments(req.attachments)

        # =========================
        # 1. ROUTER
        # =========================
        intent = route_intent_llm(
            query=req.query,
            attachments=documents,   # ⭐统一结构
            llm=rag_chain.llm
        )

        # =========================
        # 2. AUDIT MODE
        # =========================
        if intent == "audit":

            result = audit_chain.run(
                query=req.query,
                attachments=documents,   # ⭐统一结构
                kb_name=req.kb_name
            )

            return {
                "success": True,
                "mode": "audit",
                "answer": result
            }

        # =========================
        # 3. NORMAL RAG CHAT
        # =========================
        result = rag_chain.chat(
            query=req.query,
            conversation_id=req.conversation_id,
            kb_name=req.kb_name,
            top_k=req.top_k,
            attachments=documents   # ⭐统一结构
        )

        return {
            "success": True,
            "mode": "chat",
            "answer": result["answer"],
            "sources": result["sources"],
            "retrieved_docs": result["retrieved_docs"]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# STREAM API
# =====================================================
@router.post("/stream")
def stream_chat(req: ChatRequest):

    documents = normalize_attachments(req.attachments)

    intent = route_intent_llm(
        query=req.query,
        attachments=documents,
        llm=rag_chain.llm
    )

    def event_generator():

        try:

            if intent == "audit":

                result = audit_chain.run(
                    query=req.query,
                    attachments=documents,
                    kb_name=req.kb_name
                )

                yield f"data: {result}\n\n"

            else:

                for chunk in rag_chain.stream_chat(
                    query=req.query,
                    conversation_id=req.conversation_id,
                    kb_name=req.kb_name,
                    attachments=documents   # ⭐如果你 stream 支持可用
                ):
                    yield f"data: {chunk}\n\n"

        except Exception as e:
            traceback.print_exc()
            yield f"data: error: {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )