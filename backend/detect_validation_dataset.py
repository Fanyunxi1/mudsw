import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score, confusion_matrix
import joblib


# 验证验证集的分类效果
def validate_validation_data(data_path):
    # 检查验证集文件是否存在
    if not os.path.exists(data_path):
        print("验证集文件不存在！")
        return
    # 加载验证集
    try:
        print("正在加载验证集...")
        unseen_data = pd.read_csv(data_path)
        print("验证集加载完成！")
    except Exception as e:
        print(f"验证集加载失败，错误信息: {e}")
        return
    # 检查数据是否为空
    if unseen_data.empty:
        print("加载的验证集为空！请检查数据文件内容。")
        return
    # 提取标签和特征
    y_unseen = unseen_data['label'].apply(lambda x: 0 if x == 'good' else 1)
    x_unseen = unseen_data.drop(['url', 'label'], axis=1)
    # 加载之前训练好的模型
    try:
        dt = joblib.load('classifier_model/dt_best.model')
        rf = joblib.load('classifier_model/rf_best.model')
        lgbm = joblib.load('classifier_model/lgbm_best.model')
        print("模型加载成功！")
    except Exception as e:
        print(f"模型加载失败，错误信息: {e}")
        return

    # 设置 matplotlib 使用支持中文的字体
    plt.rcParams['font.family'] = 'SimHei'
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False

    # 进行预测
    dt_pred_unseen = dt.predict(x_unseen)
    rf_pred_unseen = rf.predict(x_unseen)
    lgbm_pred_unseen = lgbm.predict(x_unseen)

    # 评估验证集上的性能
    dt_unseen_accuracy = accuracy_score(y_unseen, dt_pred_unseen)
    dt_unseen_precision = precision_score(y_unseen, dt_pred_unseen)
    dt_unseen_recall = recall_score(y_unseen, dt_pred_unseen)
    dt_unseen_f1 = f1_score(y_unseen, dt_pred_unseen)
    print("dt检测验证集准确率: ", dt_unseen_accuracy)
    print("dt检测验证集精确率: ", dt_unseen_precision)
    print("dt检测验证集召回率: ", dt_unseen_recall)
    print("dt检测验证集F1值: ", dt_unseen_f1)
    # 计算dt模型的混淆矩阵
    dt_cm = confusion_matrix(y_unseen, dt_pred_unseen)
    # 可视化dt模型的混淆矩阵
    plt.figure(figsize=(6, 4))
    sns.heatmap(dt_cm, annot=True, fmt='d', cmap='Blues')
    plt.title('决策树-验证集-混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.savefig("3_confusion_matrix/dt_cm")
    plt.show()

    rf_unseen_accuracy = accuracy_score(y_unseen, rf_pred_unseen)
    rf_unseen_precision = precision_score(y_unseen, rf_pred_unseen)
    rf_unseen_recall = recall_score(y_unseen, rf_pred_unseen)
    rf_unseen_f1 = f1_score(y_unseen, rf_pred_unseen)
    print("rf检测验证集准确率: ", rf_unseen_accuracy)
    print("rf检测验证集精确率: ", rf_unseen_precision)
    print("rf检测验证集召回率: ", rf_unseen_recall)
    print("rf检测验证集F1值: ", rf_unseen_f1)
    # 计算rf模型的混淆矩阵
    rf_cm = confusion_matrix(y_unseen, rf_pred_unseen)
    # 可视化rf模型的混淆矩阵
    plt.figure(figsize=(6, 4))
    sns.heatmap(rf_cm, annot=True, fmt='d', cmap='Blues')
    plt.title('随机森林-验证集-混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.savefig("3_confusion_matrix/rf_cm")
    plt.show()

    lgbm_unseen_accuracy = accuracy_score(y_unseen, lgbm_pred_unseen)
    lgbm_unseen_precision = precision_score(y_unseen, lgbm_pred_unseen)
    lgbm_unseen_recall = recall_score(y_unseen, lgbm_pred_unseen)
    lgbm_unseen_f1 = f1_score(y_unseen, lgbm_pred_unseen)
    print("lgbm检测验证集准确率: ", lgbm_unseen_accuracy)
    print("lgbm检测验证集精确率: ", lgbm_unseen_precision)
    print("lgbm检测验证集召回率: ", lgbm_unseen_recall)
    print("lgbm检测验证集F1值: ", lgbm_unseen_f1)
    # 计算lgbm模型的混淆矩阵
    lgbm_cm = confusion_matrix(y_unseen, lgbm_pred_unseen)
    # 可视化lgbm模型的混淆矩阵
    plt.figure(figsize=(6, 4))
    sns.heatmap(lgbm_cm, annot=True, fmt='d', cmap='Blues')
    plt.title('LightGBM-验证集-混淆矩阵')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.savefig("3_confusion_matrix/lgbm_cm")
    plt.show()


def main():
    # 数据文件路径
    data_path = 'data/splited_data/Validation_features.csv'
    validate_validation_data(data_path)


if __name__ == "__main__":
    main()
