import pandas as pd
import os

new_list = []


import os



# 源文件夹路径
# 目标文件夹路径
def print_filenames(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if  name.endswith(".csv"):
                new_list.append(new_list.append( pd.read_csv(os.path.join(root, name), encoding='gbk', on_bad_lines='skip')))
                print("正在合并", name)

#src_dir 为文件夹路径，修改为你自己的
src_dir = r"E:\共享文件夹\快手csv文件"
print_filenames(src_dir)

# concat合并Pandas数据
df = pd.concat(new_list)
# 将 DataFrame 保存为 excel 文件
df.to_excel("合11并.xlsx",index=False)
print("合并完成！")

# 查看 DataFrame 的行数和列数。
rows = df.shape
print("合并后表格行数与列数：", rows)



