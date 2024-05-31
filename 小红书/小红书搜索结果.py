# -*- coding: utf-8 -*-

from DrissionPage import ChromiumPage
from DataRecorder import Recorder
import pandas as pd
from tqdm import tqdm
import time
from datetime import date
import json
from sqlalchemy import create_engine
from datetime import datetime
import pymysql
import urllib
from urllib.parse import quote

def sign_in():
    sign_in_page = ChromiumPage()
    sign_in_page.get('https://www.xiaohongshu.com')
    print("请扫码登录")
    # 第一次运行需要扫码登录
    time.sleep(20)



def search(keyword):
    global page
    page = ChromiumPage()
    page.set.NoneElement_value('')
    page.get(f'https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes')


def page_scroll_down():
    print("********下滑页面********")
    # 生成一个随机时间
    random_time = random.uniform(0.5, 1.5)
    # 暂停
    time.sleep(random_time)
    # time.sleep(1)
    # page.scroll.down(5000)
    page.scroll.to_bottom()


def get_info():
    # 定位包含笔记信息的sections
    container = page.ele('.feeds-page')
    section = container.eles('.note-item')
    # 定位文章链接
    note_link = section.ele('tag:a', timeout=0).link

    author_info = {'note_link': note_link}
    print(author_info)
    return author_info

def craw(times):
    for i in tqdm(range(1, times + 1)):
        get_info()
        page_scroll_down()



def auto_resize_column(excel_path):
    """自适应列宽度"""
    wb = openpyxl.load_workbook(excel_path)
    worksheet = wb.active
    # 循环遍历工作表中的1-2列
    for col in worksheet.iter_cols(min_col=1, max_col=2):
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
        adjusted_width = (max_length + 2) * 2
        # 使用 worksheet.column_dimensions 属性设置列宽度
        worksheet.column_dimensions[column].width = adjusted_width

        # 循环遍历工作表中的3-5列
        for col in worksheet.iter_cols(min_col=3, max_col=5):
            max_length = 0
            column = col[0].column_letter  # Get the column name

            # 使用 worksheet.column_dimensions 属性设置列宽度
            worksheet.column_dimensions[column].width = 15

    wb.save(excel_path)



if __name__ == '__main__':
    # contents列表用来存放所有爬取到的信息
    contents = []

    # 搜索关键词
    keyword = "萧煌奇"
    # 设置向下翻页爬取次数
    times = 20

    # 第1次运行需要登录，后面不用登录，可以注释掉
    # sign_in()

    # 关键词转为 url 编码
    keyword_temp_code = quote(keyword.encode('utf-8'))
    keyword_encode = quote(keyword_temp_code.encode('gb2312'))

    # 根据关键词搜索小红书文章
    search(keyword_encode)

    # 根据设置的次数，开始爬取数据
    craw(times)

    # 爬到的数据保存到本地excel文件
    # save_to_excel(contents)