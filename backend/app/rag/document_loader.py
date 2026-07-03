from app.rag.loader import load_documents


def load_attachment_documents(attachments):
    """
    将多个文件转换成结构化 documents
    不限制数量
    """

    docs = []

    for a in attachments:
        file_path = a["file_path"]
        file_name = a["file_name"]

        text = load_documents(file_path)

        docs.append({
            "file_name": file_name,
            "file_path": file_path,
            "content": text
        })

    return docs