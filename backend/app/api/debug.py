from fastapi import APIRouter, HTTPException

from app.rag.milvus_client import milvus_client

router = APIRouter()


# ==================================
# 查看统计信息
# ==================================
@router.get("/stats")
def stats():

    try:

        result = milvus_client.stats()

        print("STATS =", result)

        return result

    except Exception as e:

        import traceback

        print("\n========== STATS ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("=================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# ==================================
# 查看所有文件
# ==================================
@router.get("/files")
def list_files(
    kb_name: str = None
):

    return {
        "success": True,
        "data": milvus_client.list_files(
            kb_name=kb_name
        )
    }


# ==================================
# 查看原始chunk
# ==================================
@router.get("/documents")
def documents(
    kb_name: str = None,
    limit: int = 1000
):

    return {
        "success": True,
        "data": milvus_client.query_documents(
            kb_name=kb_name,
            limit=limit
        )
    }


# ==================================
# 删除单个文件
# ==================================
@router.delete("/file")
def delete_file(
    source: str,
    kb_name: str
):

    try:

        result = milvus_client.delete_document(
            source=source,
            kb_name=kb_name
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================
# 清空整个知识库
# ==================================
@router.delete("/kb")
def clear_kb(
    kb_name: str
):

    try:

        result = milvus_client.delete_kb(
            kb_name
        )

        return {
            "success": True,
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )