import pandas as pd
import joblib
import feature_extraction
from feature_extraction import colnames


def vote_to_detect_csv(csv_path):
    # 读取CSV
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()  # 将所有列名转换为小写
    if 'url' not in df.columns:
        raise ValueError("输入的CSV文件中必须包含一列名为 'url'")

    df['url'] = df['url'].apply(feature_extraction.wash_URL)  # 数据清洗

    extend = df['url'].apply(feature_extraction.extract_url_features)
    df = pd.concat([df, extend], axis=1)

    extend2 = df['url'].apply(feature_extraction.url_trans_token)
    df = pd.concat([df, extend2], axis=1)

    df['label'] = 0  # dummy label 占位
    df = df[colnames]

    X = df.drop(['url', 'label'], axis=1)

    # 载入模型
    dt = joblib.load('classifier_model/dt_best.model')
    lgbm = joblib.load('classifier_model/lgbm_best.model')
    rf = joblib.load('classifier_model/rf_best.model')

    # 获取预测
    dt_pred = dt.predict(X)
    lgbm_pred = lgbm.predict(X)
    rf_pred = rf.predict(X)

    # 投票机制（多数投票 >=2 认为是恶意 bad）
    final_pred = []
    for dt_p, lgbm_p, rf_p in zip(dt_pred, lgbm_pred, rf_pred):
        votes = dt_p + lgbm_p + rf_p
        if votes >= 2:
            final_pred.append('bad')
        else:
            final_pred.append('good')

    # 添加预测结果列
    result_df = pd.read_csv(csv_path)  # 重新读入原始数据以保留未删列
    result_df['result'] = final_pred

    # 筛选 bad URL 并保存
    bad_df = result_df[result_df['result'] == 'bad']
    bad_df.to_csv("detected_results.csv", index=False, encoding='utf-8')
    print(f"已将检测出的恶意URL保存到 detected_results.csv，共 {len(bad_df)} 条。")


if __name__ == "__main__":
    # 示例：你可以替换为用户上传的 CSV 文件路径
    csv_file_path = "./data/bad_urls.csv"
    vote_to_detect_csv(csv_file_path)
