import pandas as pd
import joblib
import feature_extraction
from feature_extraction import colnames


# 循环预测输入的单个URL
def vote_to_predict_single_muti(colnames):
    while True:
        print('请输入要检测的URL:')
        url = input()
        if url.lower() == 'exit':
            break
        url = feature_extraction.wash_URL(url)  # 数据清洗
        label = 0
        df = pd.DataFrame(columns=['url'], data=[url])  # 创建一个只包含 'url' 列的 DataFrame，并将用户输入的 URL 作为数据
        extend = df['url'].apply(feature_extraction.extract_url_features)  # 提取URL的特征
        df = pd.concat([df, extend], axis=1)
        extend2 = df['url'].apply(feature_extraction.url_trans_token)  # 进一步提取主机名、路径部分、参数部分以及锚部分的特征
        df = pd.concat([df, extend2], axis=1)
        df['label'] = label
        df = df[colnames]
        # 将处理后的 DataFrame 保存为 CSV 文件，不保存行索引，使用 UTF-8 编码
        df.to_csv("detect_single_muti.csv", index=False, encoding='utf-8')
        X = pd.read_csv("detect_single_muti.csv")
        X = X.drop(['url', 'label'], axis=1)

# # ----------------------------------决策树dt-------------------------------------------
#         dt = joblib.load('classifier_model/dt_best.model')
#         dt_pred = dt.predict(X)
#         print('dt_predict:', dt_pred)
#         if dt_pred[0] == 0:
#             print("决策树检测出该URL是良性的。")
#         else:
#             print("决策树检测出该URL是恶意的。")

# ----------------------------------梯度提升树lgbm-------------------------------------------
        lgbm = joblib.load('classifier_model/lgbm_best.model')
        lgbm_pred = lgbm.predict(X)
        print('lgbm_predict:', lgbm_pred)
        if lgbm_pred[0] == 0:
            print("梯度提升树检测出该URL是良性的。")
        else:
            print("梯度提升树检测出该URL是恶意的。")

# # ----------------------------------随机森林rf-------------------------------------------
#         rf = joblib.load('classifier_model/rf_best.model')
#         rf_pred = rf.predict(X)
#         print('rf_predict:', rf_pred)
#         if rf_pred[0] == 0:
#             print("随机森林检测出该URL是良性的。")
#         else:
#             print("随机森林检测出该URL是恶意的。")




if __name__ == "__main__":
    vote_to_predict_single_muti(colnames)









# import pandas as pd
# import torch
# from torch_frame.data import TensorFrame
# from feature_extraction import wash_URL, extract_url_features, url_trans_token, colnames
# from TabNet_model import TabNet  # 导入TabNet模型类
#
#
# def predict_single_url():
#     # 加载TabNet模型（假设保存的是state_dict，需手动重建模型）
#     model = TabNet(
#         out_channels=1,
#         num_layers=3,
#         split_feat_channels=50,
#         split_attn_channels=39,
#         gamma=3,
#         col_stats=None,  # 推理时无需col_stats
#         col_names_dict=None,  # 推理时无需col_names_dict
#         cat_emb_channels=47
#     ).to(torch.device('cpu'))
#     state_dict = torch.load('classifier_model/tabnet_trained.pt', map_location='cpu')
#     model.load_state_dict(state_dict)
#     model.eval()
#
#     while True:
#         print('请输入要检测的URL（输入"exit"退出）:')
#         url = input().strip()
#         if url.lower() == 'exit':
#             break
#
#         # 数据预处理（与训练时一致，）
#         cleaned_url = wash_URL(url)
#         df = pd.DataFrame({'url': [cleaned_url]})
#         df = pd.concat([df, df['url'].apply(extract_url_features)], axis=1)
#         df = pd.concat([df, df['url'].apply(url_trans_token)], axis=1)
#         df['label'] = 0  # 虚拟标签
#         df = df[colnames].drop(['url', 'label'], axis=1)  # 保留特征列
#
#         # 转换为TensorFrame对象（匹配训练时的输入格式，）
#         tf = TensorFrame.from_pandas(df)
#         tf.stypes = {col: 'numerical' for col in df.columns}  # 指定特征类型为数值型
#
#         # 模型预测（PyTorch前向传播，）
#         with torch.no_grad():
#             logits = model(tf)
#             prob = torch.sigmoid(logits).squeeze().item()
#             is_malicious = prob >= 0.5  # 阈值判断（默认0.5，可根据需求调整）
#
#         print(f"URL: {url}")
#         print("TabNet检测结果:", "恶意" if is_malicious else "良性")
#         print("-" * 50)
#
#
# if __name__ == "__main__":
#     predict_single_url()