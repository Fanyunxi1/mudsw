import pandas as pd
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

'''
从恶意URL中提取高频恶意词汇，并保存在badwords.txt中
'''

# 定义常见的顶级域名
# 在处理URL时，这些TLD将被排除
common_TLDs = ['co', 'info', 'ru', 'pl', 'ca', 'us', 'wang', 'fr',
               'org', 'it', 'au', 'jp', 'im', 'com', 'gov', 'io',
               'eu', 'me', 'nl', 'net', 'se', 'tw', 'mil', 'ch',
               'ly', 'edu', 'gl', 'cn', 'dzcom', 'to', 'cz', 'cc',
               'br', 'uk', 'be', 'es', 'no', 'in', 'tv', 'hk',
               'de', 'int', 'la', 'pro']

# 获取当前脚本的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 读取恶意URL数据，处理这些URL，生成恶意词云，并显示和保存词云图
def draw_cloud():
    bad_domains = pd.read_csv("data/bad_urls.csv") #读取恶意URL数据
    bad_domains = bad_domains.drop_duplicates() #去重
    bad_word_bags = []
    for url in bad_domains['URL']:
        str_part = [x for x in re.split('[-_/&.()<>^@!#$*=+~:;? ]', url) if x] #按照一系列特殊字符分割URL字符串，并直接过滤空字符串
        for p in str_part:
            tld_flag = False
            for tld in common_TLDs:
                if p == tld: #检查是否是常见的顶级域名，如果是，则跳过
                    tld_flag = True
                    break
            if not tld_flag: #如果不是常见的顶级域名，则加入bad_word_bags列表中
                if 2 < len(p) < 12:
                    bad_word_bags.append(p)
    text = ' '.join(bad_word_bags) #使用空格将所有片段连接起来，形成一个文本字符串
    wordcloud = WordCloud(background_color='white',  #使用WordCloud类把前面生成的文本字符串text生成词云
                          max_words=300,
                          random_state=30,
                          max_font_size=20,
                          scale=15).generate(text)
    # 显示词云图片
    plt.imshow(wordcloud)
    plt.savefig("badword_cloud.png")
    plt.axis('off')
    plt.show()


# 统计恶意url里经常出现的词,恶意高频词保存在data/badwords.txt
def count_bad_words():
    bad_domains = pd.read_csv("data/bad_urls.csv")
    bad_domains = bad_domains.drop_duplicates()
    bad_word_bags = []
    for url in bad_domains['URL']:
        str_part = [x for x in re.split('[-_/&.()<>^@!#$*=+~:;? ]', url) if x]
        for p in str_part:
            tld_flag = False
            for tld in common_TLDs:
                if p == tld:
                    tld_flag = True
                    break
            if not tld_flag:
                bad_word_bags.append(p)

    bad_words = pd.DataFrame(data=bad_word_bags, columns=['word']) #将bad_word_bags列表转换为pandas的DataFrame，列名为word
    words_bag = bad_words['word'].value_counts() #统计每个单词的次数

    words_bag_index = words_bag.index #获取words_bag的索引，即单词列表
    bad_words_in_url = []
    for i in range(len(words_bag)):
        if words_bag[i] > 10: #检查每个单词的出现频率是否大于10次
            temp_word = words_bag_index[i]
            if 2 < len(temp_word) < 20:
                bad_words_in_url.append(temp_word)
    bad_words_in_url = list(set(bad_words_in_url)) #使用set()去除列表中的重复项

    f_bad_words = open("data/badwords.txt", "w") #将恶意URL里的高频词汇记录在badwords.txt里面
    for i in range(len(bad_words_in_url)):
        f_bad_words.write(bad_words_in_url[i])
        f_bad_words.write("\n")
    f_bad_words.close()


# 从badwords.txt文件中读取全部内容，生成高频恶意词云并显示
def test_draw():
    badwords = open('data/badwords.txt', 'r').read()
    wordcloud = WordCloud(background_color='white', scale=1.5).generate(badwords)
    # 显示词云图片
    plt.imshow(wordcloud)
    plt.savefig("badword_cloud_frequency.png")
    plt.axis('off')
    plt.show()


# 从指定文件中逐行读取内容，去除每行的换行符，并将内容存储为列表返回
# feature_extraction.py会用到
def get_txt(filename):
    try:
        # 将相对路径转换为绝对路径
        abs_path = os.path.normpath(os.path.join(SCRIPT_DIR, filename))
        print(f"尝试读取文件: {abs_path}")
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = [line.strip() for line in f.readlines() if line.strip()]
            print(f"成功读取文件 {filename}，包含 {len(content)} 行内容")
            return content
    except Exception as e:
        print(f"读取文件 {filename} 时出错: {str(e)}")
        return []  # 如果出错，返回空列表


if __name__ == "__main__":
    # 读取并处理恶意URL数据，生成恶意词云
    draw_cloud()
    # 统计恶意URL中经常出现的词（高频恶意词），并保存到badwords.txt
    count_bad_words()
    # 生成高频恶意词云
    test_draw()

