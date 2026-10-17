import re
import urllib
import urllib.parse
import pandas as pd
import math
import bad_urls
import numpy as np

'''
特征提取并合并到数据集里面
特征:URL的特征;域名、路径部分、搜索部分以及锚部分的特征
'''


colnames = ['url', 'label', 'URL_a', 'URL_b', 'URL_c', 'URL_d', 'URL_e', 'URL_f',
       'URL_g', 'URL_h', 'URL_i', 'URL_j', 'URL_k', 'URL_l', 'URL_m', 'URL_n',
       'URL_o', 'URL_p', 'URL_q', 'URL_r', 'URL_s', 'URL_t', 'URL_u', 'URL_v',
       'URL_w', 'URL_x', 'URL_y', 'URL_z', 'URL_depth', 'URL_len', 'exe_flag',
       'badword_n', 'popular_n', 'URL_point', 'http_flag', 'letter_ratio',
       'at_flag', 'dig_ratio', 'special_ch', 'special_ch_kind', 'TLD_id',
       'hash_token_n', 'hostname_a', 'hostname_b', 'hostname_c',
       'hostname_ch_n', 'hostname_d', 'hostname_dig_ratio', 'hostname_e',
       'hostname_entropy', 'hostname_f', 'hostname_g', 'hostname_h',
       'hostname_i', 'hostname_is_ip', 'hostname_j', 'hostname_k',
       'hostname_l', 'hostname_len', 'hostname_letter_ratio', 'hostname_m',
       'hostname_n', 'hostname_o', 'hostname_p', 'hostname_point_n',
       'hostname_q', 'hostname_r', 'hostname_s', 'hostname_std', 'hostname_t',
       'hostname_token_n', 'hostname_u', 'hostname_v', 'hostname_w',
       'hostname_x', 'hostname_y', 'hostname_z', 'pathname_ch_kind',
       'pathname_depth', 'pathname_len', 'pathname_longest_token',
       'pathname_std', 'pathname_token_n', 'search_and_n', 'search_len',
       'search_std', 'search_token_n']

all_features = []
url_features = [
    'URL长度',
    '字母比例',
    '数字比例',
    '特殊符号的种类个数',
    '特殊字符个数',
    'URL深度(/)',
    '出现点的次数(.)',
    '存在@符号',
    '顶级域名TLD',
    '出现恶意词的次数',
    '出现流行网站名的次数',
    '出现.php或者.exe的次数',
    '在除了开头位置出现http,www的次数'
]
hostname_features = []
all_features.extend(url_features)


# 判断字符x是否为数字
def is_digit(x):
    if 48 <= ord(x) <= 57:
        return True
    return False

# 判断字符x是否为字母
def is_letter(x):
    if (97 <= ord(x) <= 122) or (65 <= ord(x) <= 90):
        return True
    return False


# 判断是否既不是数字也不是字母的特殊字符
def is_special_ch(x):
    if is_letter(x):
        return False
    elif is_digit(x):
        return False
    else:
        return True


# 判断是否含有数字
def contain_dig(str):
    for x in str:
        if 48 <= ord(x) <= 57:
            return True
    return False


# 判断是否含有英文字母
def contain_letter(str):
    for x in str:
        if (97 <= ord(x) <= 122) or (65 <= ord(x) <= 90):
            return True
    return False


# 字母夹杂数字符号的情况出现了几次
def numAndLetter(token):
    if len(token) < 2:
        return 0
    num = 0
    pre = 1 #前一个字符
    cur = 0 #当前字符
    # 0 表示字母 1表示非字母
    if is_letter(token[0]):
        pre = 0
    else:
        pre = 1
    for i in range(1, len(token)):
        if is_letter(token[i]):
            cur = 0
        else:
            cur = 1
        if cur == pre:
            continue
        else:
            num += 1
            pre = cur
    return num  # 返回交替次数


# 计算字符串的信息熵，信息熵是衡量字符串中字符随机性的指标，值越大表示字符分布越随机
def calculate_entropy(string):
    str_list = list(string)  # 将字符串转换为字符列表
    n = len(str_list)  # 计算字符串的长度
    str_list_single = list(set(str_list))  # 去重
    num_list = []
    for i in str_list_single:
        num_list.append(str_list.count(i))  # 统计每个字符在字符串中出现的次数
    entropy = 0
    for j in range(len(num_list)):
        entropy += -1 * (float(num_list[j] / n)) * math.log(float(num_list[j] / n), 2)  # 计算信息熵
    if len(str(entropy).split('.')[-1]) >= 7:
        return ('%.7f' % entropy)
    else:
        return (entropy)


# 计算字符串列表的总长度和标准差
def getLength_std(str_list):
    if len(str_list) == 0:
        return (0, 0)
    str_list_len = 0
    str_list_len_count = []
    str_list_std = 0
    for str in str_list:
        length = len(str)
        str_list_len += length  # 字符串总长度
        str_list_len_count.append(length)  # 存储每个字符串的长度
    str_arr = np.array(str_list_len_count)
    str_list_std = str_arr.std()  # 标准差
    return (str_list_len, str_list_std)  # 返回总长度和标准差


# 提取主机名、路径部分、参数部分以及锚部分的特征
def url_trans_token(url):
    decode_url = urllib.parse.unquote(url)  # 解码URL
    url = decode_url
    # 检查URL中是否包含http://或https://，如果存在且位于第一个斜杠之前，则去除协议前缀
    http_p = url.find('http://')
    if http_p != -1 and http_p < url.find('/'):
        url = url[http_p + 7:]

    https_p = url.find('https://')
    if https_p != -1 and https_p < url.find('/'):
        url = url[https_p + 8:]
    # 检查URL中是否包含www，如果存在且位于第一个点之前，则去除www前缀
    www_p = url.find('www')
    if www_p != -1 and www_p < url.find('.'):
        url = url[www_p + 4:]
    # 检查URL中是否包含其他协议（如 ftp://），如果存在且位于第一个斜杠之前，则去除协议前缀
    other_p = url.find('://')
    if other_p != -1 and other_p < url.find('/'):
        url = url[other_p + 4:]

    url_before = url
    url = url.lower()  # 将URL转换为小写

    host_tail = url.find('/')   # 找到URL中第一个斜杠的位置，提取主机名部分
    if host_tail != -1:
        url_part = url[:host_tail]  # 主机名部分，/前
    else:
        url_part = url

    pathname_depth = 0  # 路径深度
    pathname_longest_token = 0  # 路径中最长的部分
    pathname_ch_kind = 0  # 路径中字符的种类
    search_and_n = 0  # 查询参数的数量

    hostname_ch_n = 0  # 主机名中除字母、数字外字符的数量
    hostname_letter_num = 0  # 主机名中字母的数量
    hostname_dig_num = 0  # 主机名中数字的数量
    hostname_point_n = 0  # 主机名中点的数量
    hostname_is_ip = 1  # 主机名是否为IP地址

    if contain_letter(url_part):  # 检查主机名是否包含字母
        hostname_is_ip = 0  # 如果包含则主机名不是IP地址

    # hostname部分是一定存在的
    for i in range(len(url_part)):  # 遍历主机名字符串
        if is_letter(url_part[i]):
            hostname_letter_num += 1  # 统计主机名中字母的数量
        elif is_digit(url_part[i]):
            hostname_dig_num += 1  # 统计主机名数字的数量
        elif url_part[i] == '.':
            hostname_point_n += 1  # 统计主机名中.的数量
        else:
            hostname_ch_n += 1  # 统计主机名中除字母、数字外字符的数量
    hostname_dig_ratio = hostname_dig_num / len(url_part)  # 计算数字在主机名中的比例
    hostname_letter_ratio = hostname_letter_num / len(url_part)  # 计算字母在域名中的比例

    hostname = re.split('[-_/&.()<>^@!#$*=+~:; ]', url_part)   # 分割主机名
    hostname_entropy = calculate_entropy(url_part)  # 计算主机名的熵值
    while '' in hostname:
        hostname.remove('')

    # pathname、search 、hash部分可能存在
    pathname = []  # 路径部分，/到?
    search = []  # 参数部分，?到#
    hash = []  # 锚部分，#之后

    # path部分存在
    if host_tail != -1 and host_tail != len(url) - 1:  # 检查域名是否有效且不是URL的最后一个字符，确保路径部分存在
        remains = url[host_tail + 1:]  # 从域名后一个字符开始提取剩余部分
        pathname_tail = remains.find('?')  # 查找路径部分的结束位置（? 字符的位置）

        # search部分存在
        if pathname_tail != -1:

            ch_list = []
            pathname_part = remains[:pathname_tail]  # 路径部分，从/到?
            for ch_in_path in pathname_part:
                if ch_in_path == '/':
                    pathname_depth += 1  # 统计斜杠/的数量，即路径深度
                elif is_special_ch(ch_in_path):
                    ch_list.append(ch_in_path)  # 统计特殊字符数
            pathname_ch_kind = len(list(set(ch_list)))  # 计算路径中不同特殊字符的种类数

            pathname = re.split('[-_/&.()<>^@!#$*=+~:; ]', pathname_part)  # 将路径部分按特殊字符分割
            while '' in pathname:
                pathname.remove('')

            for path_token in pathname:  # 遍历路径部分的每个token，更新最长token的长度
                if len(path_token) > pathname_longest_token:
                    pathname_longest_token = len(path_token)

            search_and_hash = remains[pathname_tail + 1:]  # 提取参数部分和锚部分，？之后
            search_tail = search_and_hash.find('#')  # 查找参数部分的结束位置（#字符的位置）
            if search_tail != -1:
                search = search_and_hash[:search_tail]  # 参数部分，从?到#
            else:
                search = search_and_hash
            search_and_n = search.count('&')  # 计算查询字符串中&的数量，即查询参数的数量
            search = re.split('[-_/&.()<>^@!#$*=+~:; ]', search)
            while '' in search:
                search.remove('')

            # hash部分存在
            if search_tail != -1:
                hash.append(search_and_hash[search_tail + 1:])  # 锚部分

            # hash部分不存在
            else:
                hash = []

        # search部分不存在
        else:
            ch_list = []
            pathname_part = remains  # 没有?，剩余部分就是路径部分
            for ch_in_path in pathname_part:
                if ch_in_path == '/':
                    pathname_depth += 1  # 统计斜杠/的数量，即路径深度
                elif is_special_ch(ch_in_path):
                    ch_list.append(ch_in_path)
            pathname_ch_kind = len(list(set(ch_list)))  # 统计特殊字符的种类

            pathname = re.split('[-_/&.()<>^@!#$*=+~:; ]', remains)  # 将路径部分按特殊字符分割
            while '' in pathname:
                pathname.remove('')

            search = []
            hash = []

    # path部分不存在
    else:
        pathname = []
        search = []
        hash = []
    print(hostname, pathname, search, hash)  # 打印主机名、路径部分、参数部分和锚部分

    hostname_len, hostname_std = getLength_std(hostname)  # 计算主机名的长度和标准差

    pathname_len, pathname_std = getLength_std(pathname)  # 计算路径部分的长度和标准差

    search_len, search_std = getLength_std(search)  # 计算搜索部分的长度和标准差

    return pd.Series(
        {
            'hostname_a':url_part.count('a'),  # 返回a~z各个字母在主机名中出现的个数
            'hostname_b': url_part.count('b'),
            'hostname_c': url_part.count('c'),
            'hostname_d': url_part.count('d'),
            'hostname_e': url_part.count('e'),
            'hostname_f': url_part.count('f'),
            'hostname_g': url_part.count('g'),
            'hostname_h': url_part.count('h'),
            'hostname_i': url_part.count('i'),
            'hostname_j': url_part.count('j'),
            'hostname_k': url_part.count('k'),
            'hostname_l': url_part.count('l'),
            'hostname_m': url_part.count('m'),
            'hostname_n': url_part.count('n'),
            'hostname_o': url_part.count('o'),
            'hostname_p': url_part.count('p'),
            'hostname_q': url_part.count('q'),
            'hostname_r': url_part.count('r'),
            'hostname_s': url_part.count('s'),
            'hostname_t': url_part.count('t'),
            'hostname_u': url_part.count('u'),
            'hostname_v': url_part.count('v'),
            'hostname_w': url_part.count('w'),
            'hostname_x': url_part.count('x'),
            'hostname_y': url_part.count('y'),
            'hostname_z': url_part.count('z'),
            'hostname_token_n': len(hostname),  # 主机名中不同的token（通过点分隔的）的数量
            'hostname_len': hostname_len,  # 主机名的长度
            'hostname_ch_n': hostname_ch_n,  # 主机名中除字母、数字外字符的特殊字符数量
            'hostname_letter_ratio': hostname_letter_ratio,  # 主机名中字母的比率
            'hostname_dig_ratio': hostname_dig_ratio,  # 主机名中数字的比率
            'hostname_entropy': hostname_entropy,  # 主机名中字符的熵
            'hostname_point_n': hostname_point_n,  # 主机名中点的数量
            'hostname_is_ip': hostname_is_ip,  # 主机名是否为 IP 地址
            'hostname_std': hostname_std,  # 主机名中 token 长度的标准差
            'pathname_token_n': len(pathname),  # 路径部分中不同的 token（通过斜杠分隔的）的数量
            'pathname_len': pathname_len,  # 路径部分的长度
            'pathname_depth': pathname_depth,  # 路径部分的深度（即路径名中斜杠的数量）
            'pathname_longest_token': pathname_longest_token,  # 路径部分中最长的token的长度
            'pathname_ch_kind': pathname_ch_kind,  # 路径部分中特殊字符的种类数
            'pathname_std': pathname_std,  # 路径部分中 token 长度的标准差
            'search_token_n': len(search),  # 参数部分中不同的 token（通过&分隔的）的数量
            'search_len': search_len,  # 参数部分的长度
            'search_std': search_std,  # 参数部分中token长度的标准差
            'search_and_n': search_and_n,  # 参数部分中&的数量，即查询参数的数量
            'hash_token_n': len(hash)  # 锚部分的长度
        }
    )


# 清洗和标准化URL，移除URL中的常见前缀（如 http://、https://、www 和 ://），并确保没有/的URL以斜杠/结束
def wash_URL(url):
    url = url.lower() #转小写
    url_len = len(url)

    http_p = url.find('http://')
    if http_p != -1 and http_p < url.find('/'):
        url = url[http_p + 7:]

    https_p = url.find('https://')
    if https_p != -1 and https_p < url.find('/'):
        url = url[https_p + 8:]

    www_p = url.find('www')
    if www_p != -1 and www_p < url.find('.'):
        url = url[www_p + 4:]

    other_p = url.find('://')
    if other_p != -1 and other_p < url.find('/'):
        url = url[other_p + 4:]
    if url.find('/') == -1:
        return url+'/'
    else:
        return url


# 提取URL的特征
def extract_url_features(url):
    url = url.lower()
    url_len = len(url)

    # 去除 http://、https://、www 和其他协议前缀
    http_p = url.find('http://')
    if http_p != -1 and http_p < url.find('/'):
        url = url[http_p + 7:]

    https_p = url.find('https://')
    if https_p != -1 and https_p < url.find('/'):
        url = url[https_p + 8:]

    www_p = url.find('www')
    if www_p != -1 and www_p < url.find('.'):
        url = url[www_p + 4:]

    other_p = url.find('://')
    if other_p != -1 and other_p < url.find('/'):
        url = url[other_p + 4:]

    url_letter_ratio = 0  # URL中字母的比例
    url_dig_ratio = 0  # URL中数字的比例
    url_ch_kind_n = 0  # URL中除字母、数字、/、.和@之外的所有字符的种类数（去重后的）
    url_ch_n = 0  # URL中除字母、数字、/、.和@之外的所有字符的数量
    url_depth = 0  # URL路径深度
    url_point_n = 0  # URL中点的数量
    url_contain_at = 0  # URL中@符号的数量

    ch_list = []
    letter_num = 0
    dig_num = 0
    for i in range(len(url)):
        if is_letter(url[i]):
            letter_num += 1  # URL中字母的数量
        elif is_digit(url[i]):
            dig_num += 1  # URL中数字的数量
        elif url[i] == '/':
            url_depth += 1  # /的数量，即URL路径深度
        elif url[i] == '.':
            url_point_n += 1  # URL中点的数量
        elif url[i] == '@':
            url_contain_at += 1  # URL中@符号的数量
        else:
            ch_list.append(url[i])  # 存储除字母、数字、/、.和@之外的所有字符

    url_letter_ratio = letter_num / url_len  # URL中字母的比例
    url_dig_ratio = dig_num / url_len  # URL中数字的比例
    url_ch_n = len(ch_list)  # 除字母、数字、/、.和@之外的所有字符的数量
    url_ch_kind_n = len(list(set(ch_list)))  # URL中除字母、数字、/、.和@之外的所有字符的种类数（去重后的）

    url_port = 80  # 默认端口号是80
    parts = url.split('/')  # 将URL按/分割
    first_part = parts[0]  # 获取分割后的第一个部分，即主机名
    hostname = first_part.split('.')  # 将主机名按点分割

    if contain_dig(hostname[-1]) == False:  # 检查主机名的最后一个部分是否包含数字，如果不包含数字
        tld = hostname[-1].split(':')  # 则将主机名的最后一个部分按:分割，提取顶级域名和端口号
        url_TLD_temp = tld[0]  # 顶级域名
        if len(tld) == 2 and type(tld[1]) == type(url_port):  # 检查tld是否被成功分割为两部分，如果存在端口号且类型为整数
            url_port = tld[1]  # 更新端口号
        common_tlds = bad_urls.common_TLDs  # 存储常见的顶级域名列表
        url_TLD = 500  # 评分TLD,如果较高，则说明顶级域名不常见
        for i in range(len(common_tlds)):
            if url_TLD_temp == common_tlds[i]:  # 如果顶级域名在常见列表中
                url_TLD = i  # 更新url_TLD为列表中的索引
                break
    else:
        url_TLD = 1000  # 如果顶级域名包含数字，设置url_TLD为1000

    url_badword_n = 0  # 记录URL中包含的恶意词汇数量
    badwords = bad_urls.get_txt('data/badwords.txt')  # 从文件data/badwords.txt中读取恶意词汇列表
    for i in range(len(badwords)):
        if url.find(badwords[i]) != -1:  # 检查URL中是否包含列表中的恶意词汇
            url_badword_n += 1  # 统计URL中包含的恶意词汇数量

    url_popular_n = 0  # 记录URL中包含的流行词汇数量
    popular_web_words = bad_urls.get_txt('data/popular_web.txt')  # 从文件data/popular_web.txt中读取流行词汇列表
    for i in range(len(popular_web_words)):
        if url.find(popular_web_words[i]) != -1:  # 检查URL中是否包含列表中的流行词汇
            url_popular_n += 1  # 统计URL中包含的流行词汇数量

    url_exe_n = 0  # 记录URL中可执行文件扩展名的数量
    if url.find('.exe') != -1:
        url_exe_n += 1
    if url.find('.php') != -1:
        url_exe_n += 1

    url_http_n = 0  # 记录URL中包含http或www的数量
    if url.find('http') != -1:
        url_http_n += 1
    if url.find('www') != -1:
        url_http_n += 1

    return pd.Series(
        {
            'URL_len': url_len,  # URL的长度
            'letter_ratio': url_letter_ratio,  # URL中字母字符的比例
            'dig_ratio': url_dig_ratio,  # URL中数字字符的比例
            'special_ch_kind': url_ch_kind_n,  # URL中除字母、数字、/、.和@之外的特殊字符的种类数
            'special_ch': url_ch_n,  # URL中除字母、数字、/、.和@之外的特殊字符数
            'URL_depth': url_depth,  # URL的路径深度，即/的数量
            'URL_point': url_point_n,  # URL中点的数量
            'at_flag': url_contain_at,  # URL中@符号的数量
            'TLD_id': url_TLD,  # 评分TLD，如果较高（如1000），则说明顶级域名不常见
            'badword_n': url_badword_n,  # URL中包含的恶意词汇数量
            'popular_n': url_popular_n,  # URL中包含的流行词汇数量
            'exe_flag': url_exe_n,  # URL中包含.exe或.php等可执行文件扩展名的数量
            'http_flag': url_http_n,  # URL中包含除去开头的http或www的数量
            'URL_a': url.count('a'),  # 返回URL中a~z各个字母的数量
            'URL_b': url.count('b'),
            'URL_c': url.count('c'),
            'URL_d': url.count('d'),
            'URL_e': url.count('e'),
            'URL_f': url.count('f'),
            'URL_g': url.count('g'),
            'URL_h': url.count('h'),
            'URL_i': url.count('i'),
            'URL_j': url.count('j'),
            'URL_k': url.count('k'),
            'URL_l': url.count('l'),
            'URL_m': url.count('m'),
            'URL_n': url.count('n'),
            'URL_o': url.count('o'),
            'URL_p': url.count('p'),
            'URL_q': url.count('q'),
            'URL_r': url.count('r'),
            'URL_s': url.count('s'),
            'URL_t': url.count('t'),
            'URL_u': url.count('u'),
            'URL_v': url.count('v'),
            'URL_w': url.count('w'),
            'URL_x': url.count('x'),
            'URL_y': url.count('y'),
            'URL_z': url.count('z'),
        })


# 对输入的DataFrame中的URL列进行特征提取，并将提取的特征扩展到DataFrame中
def pandas_get_features(df):
    extend = df['url'].apply(extract_url_features)  # 对df['url']应用extract_url_features函数，提取URL的特征
    df = pd.concat([df, extend], axis=1)  # 将提取的特征按列拼接到原始DataFrame中
    extend2 = df['url'].apply(url_trans_token)  # 对df['url']应用url_trans_token函数，进一步提取主机名、路径部分、参数部分以及锚部分的特征
    df = pd.concat([df, extend2], axis=1)  # 提取的特征按列拼接到DataFrame中
    return df


# 从指定的CSV文件中读取数据，并调用pandas_get_features函数提取特征，返回包含特征的DataFrame
def csv_to_features(filename):
    data = pd.read_csv(filename)
    features = pandas_get_features(data)
    return features


if __name__ == "__main__":
    # 读取Training.csv文件并提取特征
    features_df_train = csv_to_features("data/splited_data/Training.csv")
    # 按colnames的顺序重新排列
    features_df_train = features_df_train.reindex(columns=colnames)
    # 将提取的特征保存
    features_df_train.to_csv("data/splited_data/Training_features.csv", index=False)

    # 读取Test.csv文件并提取特征
    features_df_test = csv_to_features("data/splited_data/Test.csv")
    # 按colnames的顺序重新排列
    features_df_test = features_df_test.reindex(columns=colnames)
    # 将提取的特征保存
    features_df_test.to_csv("data/splited_data/Test_features.csv", index=False)

    # 读取Validation.csv文件并提取特征
    features_df_val = csv_to_features("data/splited_data/Validation.csv")
    # 按colnames的顺序重新排列
    features_df_val = features_df_val.reindex(columns=colnames)
    # 将提取的特征保存
    features_df_val.to_csv("data/splited_data/Validation_features.csv", index=False)
