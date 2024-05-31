# 导入模块
from wordcloud import WordCloud

# 文本数据
text = "黄河是中华民族的母亲河。"
# 词云对象
wc = WordCloud()
# 生成词云
wc.generate(text)
# 保存词云文件
# wc.to_file('img01.jpg')