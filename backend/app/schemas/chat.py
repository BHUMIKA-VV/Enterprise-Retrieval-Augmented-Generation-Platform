from pydantic import BaseModel
from typing import Optional
from typing import List
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):

    query: str

    kb_name: Optional[str] = None
    conversation_id: Optional[int] = None
    
    session_id: Optional[str] = None
    top_k: int = 5

    # 🔥 新增：附件

    attachments: Optional[List[Dict[str, Any]]] = []

class SourceDocument(BaseModel):

    source: str

    content: str

    score: float


class ChatResponse(BaseModel):

    answer: str

    conversation_id: int

    sources: List[SourceDocument]