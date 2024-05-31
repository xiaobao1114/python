import jieba
import re
from collections import Counter
#设置不显示debug信息
jieba.setLogLevel(jieba.logging.INFO)
#初始化jieba分词器
jieba.initialize()

# 读取文本文件
with open('D:\sxb\Sourcetree\speed-python\小说网站\斗破苍穹.txt', 'r', encoding='utf-8') as file:
    contents = file.read()
    contents = contents.strip().replace('\n', '')
    # strip()函数删除字符串头和尾的空白字符(包括\n，\r，\t)
    # replace()函数替换所有的换行符
    contents = re.sub(r'[\W]', '', contents)
    #使用正则表达式删除所有符号

# 分词
seg_list = jieba.lcut(contents)
#利用列表推导式，过滤一个字
seg_list = [i for i in seg_list if len(i) > 1]
# 统计词频
word_count = Counter(seg_list)
# 打印词频最高的前10个词
print(word_count.most_common(10))