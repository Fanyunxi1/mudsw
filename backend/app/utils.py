import pandas as pd
import io

# def parse_csv(content: bytes):
#     df = pd.read_csv(io.BytesIO(content))
#     if 'url' not in df.columns:
#         raise ValueError("CSV must contain a 'url' column.")
#     return df['url'].tolist()

def parse_csv(content: bytes):
    try:
        # 尝试用 UTF-8 解码
        df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # 回退为常见的 GBK 编码
            df = pd.read_csv(io.BytesIO(content), encoding='gbk')
        except Exception as e:
            raise ValueError(f"无法解析 CSV 文件编码: {e}")

    if 'url' not in df.columns:
        raise ValueError("CSV must contain a 'url' column.")

    return df['url'].dropna().astype(str).tolist()


def format_results(urls, preds):
    return [{"url": url, "isMalicious": bool(p)} for url, p in zip(urls, preds)]
