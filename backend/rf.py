import pandas as pd
import os
from sklearn.metrics import make_scorer, precision_score, recall_score, accuracy_score, f1_score
import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier


# 预训练模型，并保存
def multi_machine_learing_models(data_train, data_test):
    # 训练集标签和测试集标签
    y_train = data_train['label'].apply(lambda x: 0 if x == 'good' else 1)
    y_test = data_test['label'].apply(lambda x: 0 if x == 'good' else 1)
    # 训练集数据和测试集数据的特征部分
    x_train = data_train.drop(['url', 'label'], axis=1)
    x_test = data_test.drop(['url', 'label'], axis=1)

    print('正在训练模型！')

    # 2 随机森林模型(rf)------------------------------------------------------------------------------------

    # 定义模型
    rf = RandomForestClassifier()
    # 定义超参数搜索范围
    param_grid_rf = {
        'n_estimators': [300, 400, 500],  # 随机森林中树的数量
        'max_depth': [5, 10, 15],  # 树的最大深度
        'min_samples_split': [5, 10, 15],  # 内部节点分裂所需的最小样本数
        'min_samples_leaf': [5, 10, 15],  # 叶子节点所需的最小样本数
        'max_features': [10, 20, 30],  # 每棵树的最大特征数
        'class_weight': ['balanced']
    }
    # 定义评估指（标准确度、精确度、召回率和f1值）
    scorer_rf = {
        'accuracy': make_scorer(accuracy_score),
        'precision': make_scorer(precision_score),
        'recall': make_scorer(recall_score),
        'f1': make_scorer(f1_score)
    }
    # 使用 GridSearchCV 进行超参数调优
    grid_search_rf = GridSearchCV(estimator=rf, param_grid=param_grid_rf, scoring=scorer_rf,
                                  refit='precision', cv=5, verbose=2, return_train_score=True)
    # 训练模型并搜索最佳参数
    grid_search_rf.fit(x_train, y_train)
    # 输出最佳参数
    print("RandomForest最佳参数组合: ", grid_search_rf.best_params_)
    # 使用最佳模型进行预测
    best_model_rf = grid_search_rf.best_estimator_
    y_pred = best_model_rf.predict(x_test)
    # 评估测试集上的性能
    test_accuracy = accuracy_score(y_test, y_pred)
    test_precision = precision_score(y_test, y_pred)
    test_recall = recall_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred)
    print("RandomForest测试集准确率: ", test_accuracy)
    print("RandomForest测试集精确率: ", test_precision)
    print("RandomForest测试集召回率: ", test_recall)
    print("RandomForest测试集F1值: ", test_f1)
    # 保存模型
    joblib.dump(best_model_rf, 'new_model/rf_best.model')


def main():
    # 数据文件路径
    train_data_path = 'data/splited_data/Training_features.csv'
    test_data_path = 'data/splited_data/Test_features.csv'
    # 检查数据文件是否存在
    if not os.path.exists(train_data_path) or not os.path.exists(test_data_path):
        print("数据文件不存在！")
        return
    # 加载训练数据和测试数据
    try:
        print("正在加载数据...")
        data_train = pd.read_csv(train_data_path)
        data_test = pd.read_csv(test_data_path)
        print("数据加载完成！")
    except Exception as e:
        print(f"数据加载失败，错误信息: {e}")
        return
    # 检查数据是否为空
    if data_train.empty or data_test.empty:
        print("加载的数据为空！请检查数据文件内容。")
        return
    # 调用多模型训练函数
    try:
        multi_machine_learing_models(data_train, data_test)
    except Exception as e:
        print(f"模型训练失败，错误信息: {e}")
        return
    print("模型训练完成并保存！")


if __name__ == "__main__":
    main()
