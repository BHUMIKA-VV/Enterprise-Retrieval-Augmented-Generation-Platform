from pymilvus import Collection

COLLECTION_NAME = "default"  # 你的规则库名字

def clear_default():
    collection = Collection(COLLECTION_NAME)

    # 删除所有数据（如果你用 kb_name 字段区分）
    expr = 'kb_name == "default"'

    print(f"Deleting data where {expr} ...")

    collection.delete(expr)
    collection.flush()

    print("Default KB cleared successfully.")

if __name__ == "__main__":
    clear_default()