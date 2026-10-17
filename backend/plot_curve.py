import matplotlib.pyplot as plt
import argparse
import pickle
from scipy.interpolate import interp1d
import numpy as np

# 创建命令行参数解析器
parser = argparse.ArgumentParser()
# 添加训练集文件参数
parser.add_argument('--train_file', default='eval_indicators/epoch_train_f1.pkl')
# 添加测试集文件参数
parser.add_argument('--test_file', default='eval_indicators/epoch_test_f1.pkl')
# 添加验证集文件参数
parser.add_argument('--new_file', default='eval_indicators/epoch_validation_f1.pkl')

# 解析命令行参数
args = parser.parse_args()

# 加载测试集数据
test_y_data = pickle.load(open(args.test_file, 'rb'))
# 创建测试集的 X 轴数据
test_x_data = np.array(range(len(test_y_data)))

# 加载验证集数据
new_y_data = pickle.load(open(args.new_file, 'rb'))
# 创建验证集的 X 轴数据
new_x_data = np.array(range(len(new_y_data)))

# 加载训练集数据
train_y_data = pickle.load(open(args.train_file, 'rb'))
# 创建训练集的 X 轴数据
train_x_data = np.array(range(len(train_y_data)))

# 进行插值以得到平滑曲线
test_f = interp1d(test_x_data, test_y_data, kind='cubic')
new_f = interp1d(new_x_data, new_y_data, kind='cubic')
train_f = interp1d(train_x_data, train_y_data, kind='cubic')

# 创建更密集的 X 轴数据用于绘制平滑曲线
test_x_new = np.linspace(test_x_data.min(), test_x_data.max(), 300)
test_y_new = test_f(test_x_new)
new_x_new = np.linspace(new_x_data.min(), new_x_data.max(), 300)
new_y_new = new_f(new_x_new)
train_x_new = np.linspace(train_x_data.min(), train_x_data.max(), 300)
train_y_new = train_f(train_x_new)

# 绘制训练集的平滑曲线
plt.plot(train_x_new, train_y_new, linestyle='-.', color='g', label='Train f1')
# 绘制测试集的平滑曲线
plt.plot(test_x_new, test_y_new, linestyle='--', color='r', label='Test f1')
# 绘制验证集的平滑曲线
plt.plot(new_x_new, new_y_new, linestyle='-', color='b', label='Validation f1')

# 设置图表标题和坐标轴标签
plt.title('Test, Validation and Train f1 Curves')
plt.xlabel('Epoch')
plt.ylabel('f1')

# 设置纵坐标范围
plt.ylim(0.9, 1.0)

# 显示图例
plt.legend()

# 显示网格
plt.grid(True)

# 保存图表
plt.savefig("plot_curve/f1_curves.png")

# 显示图表
plt.show()
