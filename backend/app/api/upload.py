from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from app.rag.ingestion import ingest_file

import os
import uuid
import traceback

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

ALLOWED_TYPES = [
    ".pdf",
    ".txt",
    ".docx",
    ".md",
    ".xlsx",
    ".xls"
]


# =====================================================
# Audit文件上传
# 不入向量库
# =====================================================
@router.post("/audit")
def upload_audit_file(
    file: UploadFile = File(...)
):

    ext = os.path.splitext(
        file.filename
    )[1].lower()

    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}"
        )

    try:

        file_id = str(uuid.uuid4())

        save_path = os.path.join(
            UPLOAD_DIR,
            f"{file_id}_{file.filename}"
        )

        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        with open(save_path, "wb") as f:
            f.write(content)

        print("\n========== AUDIT FILE ==========")
        print(f"filename={file.filename}")
        print(f"save_path={save_path}")
        print("mode=AUDIT")
        print("vector_store=NO")
        print("================================\n")

        return {
            "success": True,
            "filename": file.filename,
            "file_path": save_path,
            "mode": "audit"
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Audit upload failed: {str(e)}"
        )


# =====================================================
# Rules文件上传
# 入向量库
# =====================================================
@router.post("/rules")
def upload_rules_file(
    file: UploadFile = File(...),
    kb_name: str = Form("default")
):

    ext = os.path.splitext(
        file.filename
    )[1].lower()

    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}"
        )

    try:

        file_id = str(uuid.uuid4())

        save_path = os.path.join(
            UPLOAD_DIR,
            f"{file_id}_{file.filename}"
        )

        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        with open(save_path, "wb") as f:
            f.write(content)

        print("\n========== RULE FILE ==========")
        print(f"filename={file.filename}")
        print(f"save_path={save_path}")
        print(f"kb_name={kb_name}")
        print("mode=RULES")
        print("vector_store=YES")
        print("================================\n")

        # 入库
        result = ingest_file(
            file_path=save_path,
            kb_name=kb_name
        )

        print(
            f"[RULES] chunks={result.get('chunks', 0)}"
        )

        return {
            "success": True,
            "filename": file.filename,
            "file_path": save_path,
            "chunks": result.get("chunks", 0),
            "kb_name": kb_name,
            "mode": "rules"
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Rules upload failed: {str(e)}"
        )