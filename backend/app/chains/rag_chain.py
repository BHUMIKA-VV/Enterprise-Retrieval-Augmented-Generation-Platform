from app.rag.hybrid_search import HybridRetriever
from app.rag.rerank import BGEReranker

from app.services.llm_service import llm_service
from app.memory.conversation_memory import ConversationMemory

from app.prompts.rag_prompt import rag_prompt

from app.router.query_router import route_intent_llm


class RAGChain:

    def __init__(self):

        # =====================
        # Retrieval Layer
        # =====================
        self.retriever = HybridRetriever()
        self.reranker = BGEReranker()

        # =====================
        # LLM
        # =====================
        self.llm = llm_service

        # =====================
        # Memory
        # =====================
        self.memory = ConversationMemory()

        # =====================
        # LCEL Chain
        # =====================
        self.chain = rag_prompt | self.llm.llm

    def chat(
        self,
        query: str,
        conversation_id: str = None,
        kb_name: str = "default",
        top_k: int = 5,
        attachments=None
    ):

        attachments = attachments or []

        # =========================
        # 1. History
        # =========================
        history = self.memory.get_history(
            conversation_id
        )

        # =========================
        # 2. Router
        # =========================
        intent = route_intent_llm(
            query=query,
            attachments=attachments,
            llm=self.llm
        )

        # =========================
        # 3. CHAT MODE
        # =========================
        if intent == "chat":

            response = self.llm.llm.invoke(
                f"""
You are a helpful assistant.

Conversation history:
{history}

User question:
{query}

Answer naturally and concisely.
"""
            )

            answer = response.content

            self._save_memory(
                conversation_id,
                query,
                answer
            )

            return {
                "mode": "chat",
                "answer": answer,
                "sources": [],
                "retrieved_docs": []
            }

        # =========================
        # 4. AUDIT MODE
        # =========================
        if intent == "audit":

            response = self.llm.llm.invoke(
                f"""
You are a strict document reviewer.

User query:
{query}

Attachments:
{attachments}

History:
{history}

Task:
- Analyze attached documents
- Check compliance / rules / consistency
- Output structured findings
"""
            )

            answer = response.content

            self._save_memory(
                conversation_id,
                query,
                answer
            )

            return {
                "mode": "audit",
                "answer": answer,
                "sources": [],
                "retrieved_docs": []
            }

        # =========================
        # 5. RAG MODE
        # =========================
        retrieved_docs = self.retriever.retrieve(
            query=query,
            kb_name=kb_name,
            top_k=top_k
        )

        reranked_docs = self.reranker.rerank(
            query=query,
            docs=retrieved_docs
        )

        context = self.build_context(
            reranked_docs
        )

        response = self.chain.invoke(
            {
                "question": query,
                "context": context,
                "history": history
            }
        )

        answer = response.content

        self._save_memory(
            conversation_id,
            query,
            answer
        )

        # =========================
        # Sources 去重
        # =========================
        sources = []
        seen = set()

        for doc in reranked_docs:

            source = doc.get(
                "source",
                ""
            )

            if (
                source
                and source not in seen
            ):
                seen.add(source)
                sources.append(source)

        return {
            "mode": "rag",
            "answer": answer,
            "sources": sources,
            "retrieved_docs": reranked_docs
        }

    # =========================
    # Context Builder
    # =========================
    def build_context(self, docs):

        context_parts = []

        for i, doc in enumerate(docs):

            source = doc.get(
                "source",
                "unknown"
            )

            content = doc.get(
                "content",
                ""
            )

            score = round(
                float(
                    doc.get(
                        "score",
                        0
                    )
                ),
                4
            )

            context_parts.append(
                f"""
========================
规则编号：{i + 1}

规则来源文件：
{source}

检索相似度：
{score}

规则原文：
{content}

========================
"""
            )

        return "\n".join(
            context_parts
        )

    # =========================
    # Memory
    # =========================
    def _save_memory(
        self,
        conversation_id,
        query,
        answer
    ):

        if not conversation_id:
            return

        self.memory.save_message(
            conversation_id=conversation_id,
            role="user",
            content=query
        )

        self.memory.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer
        )