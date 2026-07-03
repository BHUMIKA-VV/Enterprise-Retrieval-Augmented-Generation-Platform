def route_intent_llm(query: str, attachments=None, llm=None):
    """
    Simple LLM-based router (chat / rag / audit)
    """

    attachments = attachments or []

    prompt = f"""
You are an intent classifier.

Return ONLY one word:
- chat
- rag
- audit

Rules:
- If user wants to analyze, review, check, audit document → audit
- If attachments exist → likely audit
- Otherwise → chat or rag

User Query:
{query}

Has attachments:
{bool(attachments)}

Output:
""".strip()

    if llm is None:
        return "chat"

    result = llm.invoke(prompt)

    if not result:
        return "chat"

    result = result.strip().lower()

    if "audit" in result:
        return "audit"
    if "rag" in result:
        return "rag"
    return "chat"