import torch

# 加载 .pt 文件
loaded_data = torch.load('data/splited_data_new/Training_new_feature.pt')

# 查看元组的长度
tuple_length = len(loaded_data)
print(f"元组的长度: {tuple_length}")

# 查看元组中每个元素的类型和内容
for i, element in enumerate(loaded_data):
    print(f"元素 {i} 的类型: {type(element)}")
    print(f"元素 {i} 的内容: {element}")

# 检查加载的数据是否为元组
if isinstance(loaded_data, tuple):
    # 获取元组的元素数量
    num_elements = len(loaded_data)
    print(f"元组包含 {num_elements} 个元素。")

    # 遍历元组中的每个元素
    for i, element in enumerate(loaded_data):
        element_type = type(element).__name__
        print(f"元素 {i} 的数据类型是: {element_type}")
        # 对于某些类型，还可以进一步查看其形状等信息，这里以张量为例
        if isinstance(element, torch.Tensor):
            print(f"元素 {i} 的形状是: {element.shape}")
else:
    print("加载的数据不是元组。")

# 查看第一个字典
dict_0 = loaded_data[0]
print("第一个字典的键值对:")
for key, value in dict_0.items():
    print(f"键: {key}, 值的类型: {type(value).__name__}")
    if isinstance(value, torch.Tensor):
        print(f"键 {key} 对应的值的形状: {value.shape}")
        print(f"键 {key} 对应的值: {value}")
    else:
        print(f"键 {key} 对应的值: {value}")

# 查看第二个字典
dict_1 = loaded_data[1]
print("第二个字典的键值对:")
for key, value in dict_1.items():
    print(f"键: {key}, 值的类型: {type(value).__name__}")
    if isinstance(value, torch.Tensor):
        print(f"键 {key} 对应的值的形状: {value.shape}")
        print(f"键 {key} 对应的值: {value}")
    else:
        print(f"键 {key} 对应的值: {value}")
