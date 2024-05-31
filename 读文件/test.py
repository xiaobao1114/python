import os
import shutil

def find_apk_files(src_dir, dst_dir):
    apk_name_list = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".csv"):
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_dir, file)
                print(src_file)
                shutil.copy(src_file, dst_file)

# 源文件夹路径
src_dir = r"E:\共享文件夹\app\restore"
# 目标文件夹路径
dst_dir = r'E:\共享文件夹\app\汇总'

# 如果目标文件夹不存在，创建它
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

find_apk_files(src_dir, dst_dir)