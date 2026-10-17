import pandas as pd
from feature_extraction import csv_to_features, colnames

'''
# （1）按bad/good标签分离数据
# 读取原始CSV文件
file_path = 'data/data.csv'
data = pd.read_csv(file_path)
# 分离bad和good标签的行
bad_data = data[data['label'] == 'bad']
good_data = data[data['label'] == 'good']
# 保存到不同的CSV文件
bad_data.to_csv('data/bad_good_data/bad_urls.csv', index=False)
good_data.to_csv('data/bad_good_data/good_urls.csv', index=False)


# （2）提取特征
# 读取bad/good文件并提取特征
features_df_bad = csv_to_features("data/bad_good_data/bad_urls.csv")
features_df_good = csv_to_features("data/bad_good_data/good_urls.csv")
# 按colnames的顺序重新排列
features_df_bad = features_df_bad.reindex(columns=colnames)
features_df_good = features_df_good.reindex(columns=colnames)
# 将提取的特征保存
features_df_bad.to_csv("data/bad_good_data/bad_urls_features.csv", index=False)
features_df_good.to_csv("data/bad_good_data/good_urls_features.csv", index=False)
'''

# （3）统计特征
# 读取数据
df1 = pd.read_csv('data/bad_good_data/bad_urls_features.csv')
df2 = pd.read_csv('data/bad_good_data/good_urls_features.csv')

print("---------------------------基于整体URL的特征------------------------------------")
# 基于整体URL的特征
# 要计算均值的列
common_columns_URL = ['URL_len', 'letter_ratio', 'dig_ratio', 'special_ch_kind',
                      'special_ch', 'URL_depth', 'URL_point', 'at_flag', 'TLD_id',
                      'badword_n', 'popular_n', 'exe_flag', 'http_flag', 'URL_a',
                      'URL_b', 'URL_c', 'URL_d', 'URL_e', 'URL_f', 'URL_g', 'URL_h',
                      'URL_i', 'URL_j', 'URL_k', 'URL_l', 'URL_m', 'URL_n', 'URL_o',
                      'URL_p', 'URL_q', 'URL_r', 'URL_s', 'URL_t', 'URL_u', 'URL_v',
                      'URL_w', 'URL_x', 'URL_y', 'URL_z']  # 39个

# 从两个数据集中提取这些列
df1_common_URL = df1[common_columns_URL]
df2_common_URL = df2[common_columns_URL]
# 计算两个数据集中这些列的平均值
df1_mean_URL = df1_common_URL.mean().rename('bad_url_mean')
df2_mean_URL = df2_common_URL.mean().rename('good_url_mean')
# 将结果合并到一个DataFrame中
result_df_URL = pd.concat([df1_mean_URL, df2_mean_URL], axis=1)
# 重置索引并设置列名
result_df_URL = result_df_URL.reset_index()
result_df_URL.columns = ['Column', 'bad_url_mean', 'good_url_mean']
# 在终端显示结果
print(result_df_URL)
print("--------------------------------------------------------------------------------")


print("-----------------------------基于hostname的特征----------------------------------")
# 基于hostname的特征
# 要计算均值的列
common_columns_hostname = ['hostname_token_n', 'hostname_len', 'hostname_ch_n', 'hostname_letter_ratio',
                           'hostname_dig_ratio', 'hostname_entropy', 'hostname_point_n', 'hostname_is_ip',
                           'hostname_std', 'hostname_a', 'hostname_b', 'hostname_c', 'hostname_d', 'hostname_e',
                           'hostname_f', 'hostname_g', 'hostname_h', 'hostname_i', 'hostname_j', 'hostname_k',
                           'hostname_l', 'hostname_m', 'hostname_n', 'hostname_o', 'hostname_p', 'hostname_q',
                           'hostname_r', 'hostname_s', 'hostname_t', 'hostname_u', 'hostname_v', 'hostname_w',
                           'hostname_x', 'hostname_y', 'hostname_z']  # 35个
# 从两个数据集中提取这些列
df1_common_hostname = df1[common_columns_hostname]
df2_common_hostname = df2[common_columns_hostname]
# 计算两个数据集中这些列的平均值
df1_mean_hostname = df1_common_hostname.mean().rename('bad_hostname_mean')
df2_mean_hostname = df2_common_hostname.mean().rename('good_hostname_mean')
# 将结果合并到一个DataFrame中
result_df_hostname = pd.concat([df1_mean_hostname, df2_mean_hostname], axis=1)
# 重置索引并设置列名
result_df_hostname = result_df_hostname.reset_index()
result_df_hostname.columns = ['Column', 'bad_hostname_mean', 'good_hostname_mean']
# 在终端显示结果
print(result_df_hostname)
print("--------------------------------------------------------------------------------")

print("--------------------------------基于pathname的特征-------------------------------")
# 基于pathname的特征
# 要计算均值的列
common_columns_pathname = ['pathname_token_n', 'pathname_len', 'pathname_depth', 'pathname_longest_token',
                           'pathname_ch_kind', 'pathname_std']  # 6个
# 从两个数据集中提取这些列
df1_common_pathname = df1[common_columns_pathname]
df2_common_pathname = df2[common_columns_pathname]
# 计算两个数据集中这些列的平均值
df1_mean_pathname = df1_common_pathname.mean().rename('bad_pathname_mean')
df2_mean_pathname = df2_common_pathname.mean().rename('good_pathname_mean')
# 将结果合并到一个DataFrame中
result_df_pathname = pd.concat([df1_mean_pathname, df2_mean_pathname], axis=1)
# 重置索引并设置列名
result_df_pathname = result_df_pathname.reset_index()
result_df_pathname.columns = ['Column', 'bad_pathname_mean', 'good_pathname_mean']
# 在终端显示结果
print(result_df_pathname)
print("--------------------------------------------------------------------------------")

print("------------------------------基于search的特征-----------------------------------")
# 基于search的特征
# 要计算均值的列
common_columns_search = ['search_token_n', 'search_len', 'search_std', 'search_and_n']  # 4个
# 从两个数据集中提取这些列
df1_common_search = df1[common_columns_search]
df2_common_search = df2[common_columns_search]
# 计算两个数据集中这些列的平均值
df1_mean_search = df1_common_search.mean().rename('bad_search_mean')
df2_mean_search = df2_common_search.mean().rename('good_search_mean')
# 将结果合并到一个DataFrame中
result_df_search = pd.concat([df1_mean_search, df2_mean_search], axis=1)
# 重置索引并设置列名
result_df_search = result_df_search.reset_index()
result_df_search.columns = ['Column', 'bad_search_mean', 'good_search_mean']
# 在终端显示结果
print(result_df_search)
print("--------------------------------------------------------------------------------")

print("-----------------------------基于hash的特征--------------------------------------")
# 基于hash的特征
# 要计算均值的列
common_columns_hash = ['hash_token_n']  # 1个
# 从两个数据集中提取这些列
df1_common_hash = df1[common_columns_hash]
df2_common_hash = df2[common_columns_hash]
# 计算两个数据集中这些列的平均值
df1_mean_hash = df1_common_hash.mean().rename('bad_hash_mean')
df2_mean_hash = df2_common_hash.mean().rename('good_hash_mean')
# 将结果合并到一个DataFrame中
result_df_hash = pd.concat([df1_mean_hash, df2_mean_hash], axis=1)
# 重置索引并设置列名
result_df_hash = result_df_hash.reset_index()
result_df_hash.columns = ['Column', 'bad_hash_mean', 'good_hash_mean']
# 在终端显示结果
print(result_df_hash)
print("--------------------------------------------------------------------------------")
