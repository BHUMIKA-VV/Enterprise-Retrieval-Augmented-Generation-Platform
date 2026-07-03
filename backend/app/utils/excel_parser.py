import pandas as pd


def parse_excel(file_path: str):
    """
    将 Excel 转为结构化规则列表
    """

    df = pd.read_excel(file_path)

    # 自动适配列名（防止中文/英文不一致）
    columns = list(df.columns)

    results = []

    for _, row in df.iterrows():

        item = {}

        for col in columns:
            item[col] = str(row[col]) if not pd.isna(row[col]) else ""

        results.append(item)

    return results