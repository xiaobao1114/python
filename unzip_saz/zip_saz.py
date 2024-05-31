# coding=utf-8

import shutil
import zipfile
import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import uuid
import urllib.parse

def saz_files(root_path):
    try:
        paths = []
        notes = []
        for root,dirs,files in os.walk(root_path):
            for file in files:
                if file.endswith('.saz'):
                    # print(os.path.join(root,file))
                    paths.append(os.path.join(root,file))
                    notes.append(file)
        return paths,notes
    except  Exception as e:
        print('saz_files: Error %s' % e)


# 使用zipfile模块解压saz归档文件
def saz_archive_tar(saz_path):
    try:
        # 解压到当前目录的一个子目录下
        with zipfile.ZipFile(saz_path, 'r') as saz_archive:
            saz_archive.extractall(extract_path)
            print('解压文件到： "%s"'%extract_path)
    except Exception as e:
        print('saz_archive_tar: Error %s' % e)


# 遍历解压后的目录，处理每个HTTP会话文件
def xml_to_df(extract_path):
    try:
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.endswith('.htm') :  # 客户端请求与服务器响应
                    path = os.path.join(root,file)
                    print('赋值 %s 到DataFreame'%notes)
                    html_tables = pd.read_html(path)
                    first_table_df = html_tables[0]
                    return first_table_df
    except Exception as e:
        print('xml_to_df: Error %s'%e)
def df_to_sql(df,notes):
    try:

        # 转义密码中的特殊字符
        password = urllib.parse.quote_plus('abc123!@#')

        # 创建数据库引擎，插入转义后的密码
        cnn = create_engine(f'mysql+pymysql://sibider:{password}@rm-7xv214kbc13b54959do.mysql.rds.aliyuncs.com:3306/test123?charset=utf8mb4')
        # cnn = create_engine('mysql+pymysql://root:123456789@localhost:3306/test?charset=utf8')
        date_id = datetime.today().strftime('%Y%m%d')
        uuids = [str(uuid.uuid4()) for _ in range(len(df))]
        notes = notes.replace('.saz','')
        # 将UUID的列表添加为DataFrame的新列
        df['uuid'] = uuids
        df['date_id'] = date_id
        df['notes'] = notes
        df.drop('Unnamed: 0',axis=1,inplace=True)
        df.columns = ['id', 'code', 'protocol_id', 'host', 'url', 'link', 'Cache', 'requesttype', 'Process',
                      'note', 'custom', 'X-HostIP', 'RequestSize', 'ResponseSize', 'Referer',
                      'User-Agent', 'Start', 'uuid', 'date_id', 'notes']
        df.to_sql('ods_speed_saz_dpi', cnn, if_exists='append', index=False)
        print( df.columns)
    except Exception as e:
        print('df_to_sql: Error %s'%e)


def clean_up(saz_archive):
    try:
        if os.path.exists(saz_archive):
            shutil.rmtree(saz_archive)
            print('删除 saz 解析文件')
    except Exception as e:
        print('删除文件：Error :%s'%e)



if __name__ == '__main__':
    root_path = "saz话单"
    extract_path = "saz_archive/"
    saz_paths,notes = saz_files(root_path)
    for saz_path, notes in zip(saz_paths, notes):
        saz_path_re = saz_path.replace('.saz','')
        extract_path = '%s%s'%(extract_path,saz_path_re)
        saz_archive_tar(saz_path)
        extract_path = "saz_archive/"
        df = xml_to_df(extract_path)
        df_to_sql(df,notes)
        clean_up(extract_path)