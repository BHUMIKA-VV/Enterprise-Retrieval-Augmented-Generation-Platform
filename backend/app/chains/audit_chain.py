from app.utils.file_parser import parse_file


class AuditChain:

    def __init__(self, rag_chain, llm):
        self.rag_chain = rag_chain
        self.llm = llm

    # =====================================================
    # MAIN ENTRY
    # =====================================================
    def run(self, query, attachments, kb_name="default"):

        # =========================
        # 1. LOAD DOCUMENTS
        # =========================
        documents = self._load_documents(attachments)

        print("\n========== AUDIT DEBUG ==========")
        print("attachments:", attachments)
        print(f"document_count={len(documents)}")
        print("================================\n")

        if not documents:
            documents = [{
                "file_name": "unknown",
                "content": query
            }]

        # =========================
        # MODE CONTROL (CRITICAL FIX)
        # =========================
        is_multi_doc = len(documents) > 1
        mode = "MULTI" if is_multi_doc else "SINGLE"

        # =========================
        # RULE RETRIEVAL (Milvus)
        # =========================
        rules_docs = self.rag_chain.retriever.retrieve(
            query=query,
            kb_name=kb_name,
            top_k=8
        )

        rules_text = self.rag_chain.build_context(rules_docs)

        # =========================
        # DOCUMENT CONTEXT
        # =========================
        doc_text = self._build_documents_text(documents)

        # =========================
        # PROMPT
        # =========================
        prompt = self._build_prompt(
            query=query,
            rules_text=rules_text,
            doc_text=doc_text,
            mode=mode
        )

        # =========================
        # LLM CALL
        # =========================
        response = self.llm.llm.invoke(prompt)

        return response.content

    # =====================================================
    # LOAD DOCUMENTS
    # =====================================================
    def _load_documents(self, attachments):

        docs = []

        for a in attachments:

            file_path = a.get("file_path")
            file_name = a.get("file_name", "unknown")

            if not file_path:
                continue

            try:
                content = parse_file(file_path)
            except Exception as e:
                print(f"[ERROR parsing file] {file_name}: {e}")
                content = ""

            docs.append({
                "file_name": file_name,
                "content": content
            })

        return docs

    # =====================================================
    # FORMAT DOCUMENTS
    # =====================================================
    def _build_documents_text(self, documents):

        blocks = []

        for i, doc in enumerate(documents):

            blocks.append(f"""
========================
文档 {i + 1}
文件名：{doc.get('file_name', 'unknown')}

内容：
{doc.get('content', '')}
========================
""")

        return "\n".join(blocks)

    # =====================================================
    # FINAL PROMPT (STRICT VERSION)
    # =====================================================
    def _build_prompt(self, query, rules_text, doc_text, mode):

        mode_rule = {
            "SINGLE": """
【MODE = SINGLE-DOCUMENT】
- 严禁跨文档分析
- 只能使用当前文档自身内容
- 不允许引用“其他文档”
- 不允许时间对比
- 不允许数据对比
- 缺失字段必须明确标记：❌“信息缺失”
""",

            "MULTI": """
【MODE = MULTI-DOCUMENT】
- 允许跨文档分析
- 必须做时间 / 数据 / 逻辑 / 人员一致性检查
- 必须输出冲突证据
"""
        }[mode]

        return f"""
你是企业级合规审计系统（严格模式）。

========================
{mode_rule}

========================
【用户问题】
========================
{query}

========================
【规则（Milvus检索结果）】
========================
{rules_text}

========================
【待审核文档】
========================
{doc_text}

========================
【强制要求（VERY IMPORTANT）】
========================

1. 单文档必须做“字段完整性检查”：
   - 是否缺少：时间 / 签字 / 项目名称 
   - 缺失必须明确列出（不能忽略）

2. 单文档合规检查：
   - 只匹配“明确相关规则”

3. MULTI模式才允许跨文档：
   - 时间顺序
   - 数据一致性
   - 逻辑冲突

4. 不允许推测：
   - 没有字段 = 直接标记“缺失”
   - 不允许解释合理性
5. 如果上传的是不同项目的同一类型文档：
   - 重点检查同一项目周期内有无人员复用
========================
【输出格式（严格）】
========================

风险等级：低 / 中 / 高

━━━━━━━━━━━━━━━━━━━━

不符合项：

- 【文档1】xxx.docx
  问题类型：缺失 / 违规 / 异常
  违反规则来源：xxx（或“字段检查”）
  问题描述：xxx
  对比内容：
    - 规则要求：xxx
    - 实际内容：xxx / ❌缺失

━━━━━━━━━━━━━━━━━━━━

跨文档冲突：

（仅 MULTI-MODE 输出）

- 类型：时间 / 数据 / 逻辑 / 人员 / 状态
  涉及文档：
    - A.docx：xxx
    - B.docx：xxx
  说明：
    xxx

━━━━━━━━━━━━━━━━━━━━

原因说明：

- 逐条说明

━━━━━━━━━━━━━━━━━━━━

整改建议：

- 修复建议
"""