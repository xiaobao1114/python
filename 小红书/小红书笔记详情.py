# -*- coding: utf-8 -*-

from DrissionPage import ChromiumPage, ChromiumOptions
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


# 1、 todo 登录
def sign_in():
    sign_in_page = ChromiumPage()
    sign_in_page.set.NoneElement_value('')
    sign_in_page.get('https://www.xiaohongshu.com')
    print("请扫码登录")
    # 第一次运行需要扫码登录
    time.sleep(20)


# 2、从txt文件中读取所有笔记链接
def read_urls_from_txt(path):
    with open(path, 'r') as file:
        urls = [line.strip() for line in file.readlines()]
    return urls


# 3、打开小红书笔记详情页
def open_url(url,prot):
    global page
    co = ChromiumOptions().set_local_port(prot)
    page = ChromiumPage(co)

    # page = ChromiumPage()
    # page.set.NoneElement_value('')
    # page.set.load_mode.eager()
    page.get(f'{url}')


# 4、采集页面数据
def get_note_contents(page, url):
    note_link = url
    div_author = page.ele('.author-container', timeout=0)
    div_info = div_author.ele('.info', timeout=0)
    # 作者名字
    author_name = div_info.ele('.username', timeout=0).text
    print(author_name)
    # 作者主页链接
    author_link = div_info.eles('tag:a', timeout=0)[0].link
    # 提取笔记内容
    # 笔记标题
    note_title = page.ele('#detail-title', timeout=0).text
    # 笔记内容
    note_desc = page.ele('#detail-desc', timeout=0).text
    # 笔记日期和地区
    date_city = page.ele('@class:date', timeout=0).text
    # 点赞 评论数 收藏
    like_count = page.ele(
        'xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[1]/span[1]/span[2]', timeout=0).text
    collect_count = page.ele(
        'xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[1]/span[2]/span', timeout=0).text
    chat_count = page.ele('xpath://*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[2]/div/div[1]/span[3]/span',
                          timeout=0).text
    author_info = {'author_name': author_name, 'author_link': author_link,
                   'note_title': note_title, 'note_desc': note_desc, 'date_city': date_city,
                   'like_count': like_count, 'collect_count': collect_count, 'chat_count': chat_count,
                   'note_link': note_link}
    return author_info


def get_note_page_info(content_ids):
    note_contents = []
    num = 1
    prot = 9248
    content_ = []
    for content_id in tqdm(content_ids):
        time.sleep(2)
        try:
            url = ('https://www.xiaohongshu.com/explore/' + str(content_id))
            print(url)
            # 采集笔记详情，返回一个note_contents字典
            # 访问url
            open_url(url,prot)
            # 提取作者信息、笔记内容、提取点赞、收藏、评论数
            note_content = get_note_contents(page, url)
            note_content['content_id'] = content_id
            note_content['current_date'] = current_date
            print(note_content)
            note_contents.append(note_content)
            if num % 10000 == 0:
                print(f"遍历到：{num},开始写入数据库")
                df = pd.DataFrame(note_contents)
                df.to_sql('ods_static_app_social_xhs_contents_ft', cnn, if_exists='append', index=False)
                time.sleep(600)
                prot += 1
            if num % 20001 == 0:
                time.sleep(6000)
            num +=1
        except Exception as e:
            print("error : " + str(e))
            content_.append(content_id)
            pdcsv = pd.DataFrame(content_)
            pdcsv.to_csv('网页不存在.csv', mode='a', header=False, index=False)
            num +=1
            if num % 30001 == 0 :
                break
    return note_contents


def read_mysql(cnn):
    df1 = pd.read_sql_query("select t.content_id  from  ods_static_app_social_jq_kol_id_ft t  where site = '4' ", cnn)
    df2 = pd.read_sql_query('select content_id  from test123.ods_static_app_social_xhs_contents_ft group by content_id', cnn)
    df1['content_id'] = df1['content_id'].apply(lambda x: x.lstrip('k'))
    df3 = pd.read_csv('网页不存在.csv')
    # df3 = pd.read_sql_query('select *  from test123.ods_static_app_social_xhs_contents_ft ', cnn)
    # 过滤已经爬取的数据
    filtered_df = df1[~df1['content_id'].isin(df2['content_id'])]
    # 过滤 404的笔记
    filtered_df_new = filtered_df[~filtered_df['content_id'].isin(df3['0'])]
    # 计算这些行的数量
    print(df1.count())
    print(df2.count())
    print(df3.count())
    print(filtered_df_new.count())
    content_ids = []
    for content_id in filtered_df_new['content_id'].drop_duplicates():
        content_ids.append(str(content_id))
    return content_ids


if __name__ == '__main__':
    # 第1次运行需要登录，后面不用登录，可以注释掉
    # sign_in()

    # 获取当前日期
    current_date = date.today()
    print(f"当前日期 : {current_date}")
    # 设置要采集的笔记链接
    # 从txt文件读取urls
    # note_urls = read_urls_from_txt('test.txt')

    # 创建数据库引擎，插入转义后的密码
    password = urllib.parse.quote_plus('abc123!@#')
    cnn = create_engine(f'mysql+pymysql://sibider:{password}@rm-7xv214kbc13b54959do.mysql.rds.aliyuncs.com:3306/test123?charset=utf8mb4')
    # # 从mysql读取urls

    content_ids = read_mysql(cnn)
    get_note_page_info(content_ids)




# 751361 20240521
# 744361  20240521
# 738359  20240524
# 734359  20240527
# 729150  20240528
# 728166  20240529
# 724535  20240530