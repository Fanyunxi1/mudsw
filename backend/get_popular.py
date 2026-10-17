import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt


'''
从世界前500的知名URL中获取流行词
'''


# 获取顶级域名TLD
def getTLD(str):
    str_part = str.split('.')
    tld0 = str_part[-1].split(':')
    tld = tld0[0]
    return tld

world_top_sites = []
TLDs = []
common_TLD_in_Top = []

# 获取世界前500的URL
top_domains = pd.read_csv("data/World_Top_500.csv")
for url in top_domains['URL']:
    world_top_sites.append(url.lower())
top_sites = list(set(world_top_sites))
num_of_Top_sites = len(top_sites)

# 记录世界前500的URL中的TLD
for url in top_sites:
    tld_of_top_site = getTLD(url)
    TLDs.append(tld_of_top_site)
common_TLDs = list(set(TLDs))

# 记录世界前500的URL中的常见的TLD（出现次数>=3次）
for i in range(0, len(common_TLDs)):
    count = TLDs.count(common_TLDs[i])
    if count > 2:
        common_TLD_in_Top.append(common_TLDs[i])

top_words_source = [] #词来源的URL的索引
top_domain_use_words = [] #世界前500的URL里面的词（除去顶级域名）,流行词

# 统计世界前500的URL里面的词（除去顶级域名）
index = 0
for url in top_sites:
    url_block = url.split('.')
    url_block.pop(-1)  # 去掉最后一个位置的.com之类的顶级域名
    for block in url_block:
        if (len(block) > 2):  # 长度太短的词就不考虑了
            flag = 0
            for fix in common_TLD_in_Top:
                if block == fix:
                    flag += 1
                    break
                else:
                    pass
            if flag == 0:
                top_domain_use_words.append(block) # 记录除顶级域名外的词
                top_words_source.append(index) # 记录词来源的URL的索引
    index += 1
#将top_domain_use_words列表中的单词用空格连接成一个字符串text，作为词云的输入
text = ' '.join(top_domain_use_words)
wordcloud = WordCloud(background_color='white',
                      max_words=300,
                      random_state=30, #设置随机种子，确保每次生成的词云一致
                      max_font_size=20,
                      scale=15).generate(text)
# 显示流行词云图片
plt.imshow(wordcloud)
plt.savefig("popular_cloud.png")
plt.axis('off')
plt.show()
top_domain_use_words = list(set(top_domain_use_words))

# 保存流行词，即世界前500知名URL里面的词
def save():
    f_pupular_words = open("data/popular_web.txt", "w")
    for i in range(len(top_domain_use_words)):
        f_pupular_words.write(top_domain_use_words[i])
        f_pupular_words.write("\n")
    f_pupular_words.close()
