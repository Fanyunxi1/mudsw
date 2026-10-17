import torch, joblib
import pandas as pd
from feature_extraction import extract_url_features, url_trans_token, wash_URL, colnames

class URLScannerModel:
    def __init__(self):
        self.lgbm = joblib.load("model/lgbm_best.model")

    def predict(self, url: str) -> bool:
        url = wash_URL(url)  # 数据清洗
        label = 0
        df = pd.DataFrame(columns=['url'], data=[url])  # 创建一个只包含 'url' 列的 DataFrame，并将用户输入的 URL 作为数据
        extend = df['url'].apply(extract_url_features)  # 提取URL的特征
        df = pd.concat([df, extend], axis=1)
        extend2 = df['url'].apply(url_trans_token)  # 进一步提取主机名、路径部分、参数部分以及锚部分的特征
        df = pd.concat([df, extend2], axis=1)
        df['label'] = label
        df = df[colnames]
        # 将处理后的 DataFrame 保存为 CSV 文件，不保存行索引，使用 UTF-8 编码
        df.to_csv("detect_single_muti.csv", index=False, encoding='utf-8')
        X = pd.read_csv("detect_single_muti.csv")
        X = X.drop(['url', 'label'], axis=1)

        lgbm_pred = self.lgbm.predict(X)
        return int(lgbm_pred[0]) == 1

    def predict_batch(self, urls: list[str]) -> list[bool]:
        cleaned_urls = [wash_URL(url) for url in urls]
        df = pd.DataFrame({'url': cleaned_urls})
        extend = df['url'].apply(extract_url_features)
        df = pd.concat([df, extend], axis=1)
        extend2 = df['url'].apply(url_trans_token)
        df = pd.concat([df, extend2], axis=1)
        df['label'] = 0
        df = df[colnames]
        X = df.drop(['url', 'label'], axis=1)
        X = X.astype(float)
        preds = self.lgbm.predict(X)
        return [bool(p) for p in preds]
