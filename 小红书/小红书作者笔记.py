from DrissionPage import ChromiumPage
from DataRecorder import Recorder
import pandas as pd
from tqdm import tqdm
import time
import random
import re
import openpyxl
import os
import math

def countdown(n):
    for i in range(n, 0, -1):
        print(f'\r倒计时{i}秒', end='')  # \r让光标回到行首 ，end=''--结束符为空，即不换行
        time.sleep(1)  # 让程序等待1秒
    else:
        print('\r倒计时结束')

def sign_in():
    sign_in_page = ChromiumPage()
    sign_in_page.get('https://www.xiaohongshu.com')
    # 第一次运行需要扫码登录
    print("请扫码登录")
    # 倒计时30s
    countdown(30)

def open(url):
    global page, user_name
    page = ChromiumPage()
    page.get(f'{url}')
    # 页面最大化
    page.set.window.max()

    # 定位作者信息
    user = page.ele('.info')
    # 作者名字
    user_name = user.ele('.user-name', timeout=0).text



def get_info():
    # 定位包含笔记信息的sections
    container = page.ele('.feeds-container')
    sections = container.eles('.note-item')

    notes = []

    for section in sections:  # 迭代每个笔记段落
        # 笔记类型
        if section.ele('.play-icon', timeout=0):
            note_type = "视频"
        else:
            note_type = "图文"
        # 文章链接
        note_link = section.ele('tag:a', timeout=0).link
        # 标题
        title = section.ele('.title', timeout=0).text  # footer变回section
        # 作者
        author_wrapper = section.ele('.author-wrapper')  # footer变回section
        # 点赞
        like = author_wrapper.ele('.count').text

        note = {'作者': user_name, '笔记类型': note_type, '标题': title, '点赞数': like, '笔记链接': note_link}
        notes.append(note)
        # 写入数据
        r.add_data(notes)
    print(notes)
    # 写入数据需要根据你自己的需求来决定，但是这里你可能需要使用Recorder类来做类似的操作。使用之前，你需要实例化这个类，然后你才能使用add_data方法。例如: r = Recorder(); r.add_data(notes)

def page_scroll_down():
    print(f"********下滑页面********")
    page.scroll.to_bottom()
    # 生成一个1-2秒随机时间
    random_time = random.uniform(1, 2)
    # 暂停
    time.sleep(random_time)

# 设置向下翻页爬取次数
def crawler(times):
    global i
    for i in tqdm(range(1, times + 1)):
        get_info()
        page_scroll_down()


def re_save_excel(file_path):
    # 读取excel文件
    df = pd.read_excel(file_path)
    print(f"总计向下翻页{times}次，获取{df.shape[0]}条笔记（含重复获取）。")
    df['点赞数'] = df['点赞数'].astype(int)
    # 删除重复行
    df = df.drop_duplicates()
    # 按点赞 降序排序
    df = df.sort_values(by='点赞数', ascending=False)
    # 文件路径
    final_file_path = f"小红书作者主页所有笔记-{author}-{df.shape[0]}条.xlsx"
    df.to_excel(final_file_path, index=False)
    print(f"总计向下翻页{times}次，笔记去重后剩余{df.shape[0]}条，保存到文件：{final_file_path}。")
    print(f"数据已保存到：{final_file_path}")


def auto_resize_column(excel_path):
    """自适应列宽度"""
    wb = openpyxl.load_workbook(excel_path)
    worksheet = wb.active
    # 循环遍历工作表中的1-3列
    for col in worksheet.iter_cols(min_col=1, max_col=5):
        max_length = 0
        # 列名称
        column = col[0].column_letter
        # 循环遍历列中的所有单元格
        for cell in col:
            try:
                # 如果当前单元格的值长度大于max_length，则更新 max_length 的值
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        # 计算调整后的列宽度
        adjusted_width = (max_length + 5)
        # 使用 worksheet.column_dimensions 属性设置列宽度
        worksheet.column_dimensions[column].width = adjusted_width
    wb.save(excel_path)


if __name__ == '__main__':
    # 1、第1次运行需要登录，需要执行sign_in()步骤。第2次之后不用登录，可以注释掉sign_in()步骤。
    sign_in()

    # 2、设置主页地址url
    author_url = "https://www.xiaohongshu.com/user/profile/60bc91d4000000000100497f"

    # 3、设置向下翻页爬取次数
    # 根据小红书作者主页“当前发布笔记数”计算浏览器下滑次数。
    # “当前发布笔记数” 获取方法参考https://www.sohu.com/a/473958839_99956253
    # note_num是笔记数量
    note_num = 62
    # times是计算得到的翻页次数，笔记数量除以20，调整系数，再向上取整
    times = math.ceil(note_num / 20 * 1.1)
    print(f"需要执行翻页次数为：{times}")

    # 4、设置要保存的文件名file_path
    # 获取当前时间
    current_time = time.localtime()
    # 格式化当前时间
    formatted_time = time.strftime("%Y-%m-%d %H%M%S", current_time)
    # 初始化文件
    init_file_path = f'小红书作者主页所有笔记-{formatted_time}.xlsx'
    r = Recorder(path=init_file_path, cache_size=100)

    # 下面不用改，程序自动执行
    # 打开主页
    open(author_url)

    # 根据设置的次数，开始爬取数据
    # crawler(times)

    # 避免数据丢失，爬虫结束时强制保存excel文件
    # r.record()

    # 数据去重、排序，另存为新文件
    # re_save_excel(init_file_path)