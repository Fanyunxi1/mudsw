from sklearn.model_selection import train_test_split
import pandas as pd

'''
划分训练集、测试集和验证集，并分别保存在Training.csv、Test.csv和Validation.csv中
'''


def divide_data():
    origin_data_filename = "data/data.csv"
    data = pd.read_csv(origin_data_filename)
    labels = data['label'].apply(lambda x: 0 if x == 'good' else 1)  # 使用apply函数将标签转换为二进制形式：‘good’ 标签转换为 0，‘bad’ 标签转换为 1
    # 第一步：划分 70% 训练集和 30% 临时数据集
    train_data, temp_data, train_labels, temp_labels = train_test_split(
        data, labels, test_size=0.3, stratify=labels, random_state=42
    )

    # 第二步：将临时数据集划分为 50% 测试集和 50% 验证集
    test_data, val_data, test_labels, val_labels = train_test_split(
        temp_data, temp_labels, test_size=0.5, stratify=temp_labels, random_state=42
    )
    print('划分好啦！')

    # 计算标签为 1 (bad) 的比例，验证是否成功分层划分
    train_one_ratio = train_labels.value_counts(normalize=True).get(1, 0)
    test_one_ratio = test_labels.value_counts(normalize=True).get(1, 0)
    val_one_ratio = val_labels.value_counts(normalize=True).get(1, 0)
    print(f"训练集中标签为 1 (bad) 的比例: {train_one_ratio:.2%}")
    print(f"测试集中标签为 1 (bad) 的比例: {test_one_ratio:.2%}")
    print(f"验证集中标签为 1 (bad) 的比例: {val_one_ratio:.2%}")

    train_data.to_csv("data/splited_data/Training.csv", index=False, encoding='utf-8')  # 保存训练集
    test_data.to_csv("data/splited_data/Test.csv", index=False, encoding='utf-8')  # 保存测试集
    val_data.to_csv("data/splited_data/Validation.csv", index=False, encoding='utf-8')  # 保存验证集
    print('DONE!')


def read_data():
    filename_train = "data/splited_data/Training.csv"  # 训练集
    filename_test = "data/splited_data/Test.csv"  # 测试集
    filename_val = "data/splited_data/Validation.csv"  # 验证集
    data_train = pd.read_csv(filename_train)
    data_test = pd.read_csv(filename_test)
    data_val = pd.read_csv(filename_val)
    return (data_train, data_test, data_val)  # 返回读取的训练集、测试集和验证集数据


if __name__ == "__main__":
    divide_data()
    read_data()