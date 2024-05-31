import pandas as pd
import os
import sys
import json
import paramiko
import numpy as np
import urllib
from sqlalchemy import create_engine

# 定义函数ssh,把操作内容写到函数里


import pymysql


class RemoteClient:
    def __init__(self, remote_host, username, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(remote_host, username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())

    def put_file(self, local_file_path, remote_file_path):
        self.sftp.put(local_file_path, remote_file_path + os.path.basename(local_file_path))

    def exec_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode('utf-8', errors='ignore')

    def close(self):
        self.client.close()






def sftp_put(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.apk'):
                local_path = os.path.join(root, file)
                remote_path = '/home/speed/apk/'
                print('上传： ' + os.path.basename(file))
                client.put_file(local_path, remote_path)





class UseMysql(object):
    def __init__(self, user, passwd, db, host="rm-7xv214kbc13b54959do.mysql.rds.aliyuncs.com", port=3306):
        self.db = db
        self.conn = pymysql.connect(
            host=host, user=user, passwd=passwd, db=db, port=port, charset='utf8')  # 链接数据库
        self.cursor = self.conn.cursor()

    def table_exists(self, table_name) -> bool:
        """判断表是否存在
        :param table_name: 表名
        :return: 存在返回True，不存在返回False
        """
        sql = "show tables;"
        self.cursor.execute(sql)
        tables = self.cursor.fetchall()
        for _t in tables:
            if table_name == _t[0]:
                return True
        return False

    def create_table(self, data: dict, table_name):
        """创建表"""
        # 构造数据库
        sql_key_str = ''
        columnStyle = ' text'  # 数据库字段类型
        for key in data.keys():
            sql_key_str = sql_key_str + ' ' + key + columnStyle + ','
        self.cursor.execute("CREATE TABLE %s (%s)" % (table_name, sql_key_str[:-1]))
        # 添加自增ID
        self.cursor.execute("""ALTER TABLE `{}` \
                    ADD COLUMN `id` INT NOT NULL AUTO_INCREMENT FIRST, \
                    ADD PRIMARY KEY (`id`);"""
                            .format(table_name))
        # 添加创建时间
        self.cursor.execute(
            """ALTER TABLE {} ADD join_time timestamp NULL DEFAULT current_timestamp();""".format(table_name))

    def write_dict(self, data: dict, table_name):
        """
        写入mysql，如果没有表，创建表
        :param data: 字典类型
        :param table_name: 表名
        :return:
        """
        if not self.table_exists(table_name):
            self.create_table(data, table_name)
        sql_key = ''  # 数据库行字段
        sql_value = ''  # 数据库值
        for key in data.keys():  # 生成insert插入语句
            sql_value = (sql_value + '"' + ''.join(data[key]) + '"' + ',')
            sql_key = sql_key + ' ' + key + ','

        self.cursor.execute(
            "INSERT INTO %s (%s) VALUES (%s)" % (table_name, sql_key[:-1], sql_value[:-1]))
        self.conn.commit()  # 提交当前事务


def dict_list(app_info):
    for key, value in app_info.items():
        app_info[key] = value.split(' \n')



def to_lists(iterator,package_name):
    lists1 = []

    if type(iterator) == dict:
        for value in iterator.values():
            for i in value:
                lists = [package_name, i]
                lists1.append(lists)

    else :
        for i in iterator:
            lists = [package_name, i]
            lists1.append(lists)
    return lists1



def save_json(dict_,apkname):
    with open(f'{path}\\{apkname}.json', 'w', encoding='utf-8') as f:
        json.dump(dict_, f, ensure_ascii=False)


def apk_lists():
    # 读apk文件
    sexec_upload = ''' 
                ls /home/speed/apk
            '''
    # stdapk = sshExeCMD(sexec_upload)
    stdapk = client.exec_command(sexec_upload)
    apk_list = stdapk.split('\n')
    apk_lists = [x for x in apk_list if x.endswith('.apk')]
    return apk_lists


def MobSF_dict_(apk,API_KEY):
    ## Upload File API 上传文件 API
    sexec_upload = f'''
                    curl -F 'file=@/home/speed/apk/{apk}' http://localhost:8000/api/v1/upload -H "Authorization:{API_KEY}"
                '''

    # gethash = sshExeCMD(sexec_upload)
    gethash = client.exec_command(sexec_upload)
    ## Scan File API 扫描文件 API
    dict_ = json.loads(gethash)
    hash = dict_['hash']
    sexec = f'curl -X POST --url http://localhost:8000/api/v1/scan --data "hash={hash}" -H "Authorization:{API_KEY}"'
    # sshExeCMD(sexec)
    client.exec_command(sexec)
    ## Generate JSON Report API 生成 JSON 报表 API
    sexec = f'curl -X POST --url http://localhost:8000/api/v1/report_json --data "hash={hash}" -H "Authorization:{API_KEY}"'
    # getjson = sshExeCMD(sexec)
    getjson = client.exec_command(sexec)
    dict_ = json.loads(getjson)
    apkname = apk.replace('.apk', '')
    save_json(dict_, apkname)
    client.close()
    return dict_

def df_tomysql(list,Table):
    password = urllib.parse.quote_plus('abc123!@#')
    cnn = create_engine(
        f'mysql+pymysql://sibider:{password}@rm-7xv214kbc13b54959do.mysql.rds.aliyuncs.com:3306/test123?charset=utf8mb4')
    if Table == 'ods_static_app_social_hosts_ft':
        df_ = pd.DataFrame(list, columns=['package_name', 'hosts'])
    elif Table == 'ods_static_app_social_activitie_ft':
        df_ = pd.DataFrame(list, columns=['package_name', 'activities'])
    df_.to_sql(Table, cnn, if_exists='append', index=False)

def report_json(API_KEY):
    #todo 遍历文件夹得到app名字
    apk_list = apk_lists()
    for apk in apk_list:
        print("解析： " + ''.join(apk))
        #todo 解析apk得到json文件，并且转换成dict
        dict_ = MobSF_dict_(apk,API_KEY)

        #todo 提取 info、domains、activities信息
        # 定义需要保存的键的列表
        dict_hosts = {'keys':list(dict_['domains'].keys())}

        dict_activities = dict_['activities']
        keys_to_save = ['app_name', 'file_name', 'size', 'package_name']

        package_name = dict_['package_name']
        dict_info = {}

        # 遍历每个需要保存的键，获取并保存其对应的值
        # 给 dict_info 赋值，并且对values转list
        for key in keys_to_save:
            dict_info[key] = dict_.get(key, 'none')
        dict_list(dict_info)
        app_domain = to_lists(dict_hosts, package_name)
        app_activitie = to_lists(dict_activities, package_name)

        print("  --------------- 写入数据库ing ---------------------" )
        print(dict_info)
        print(app_domain)
        print(app_activitie)
        #todo info、domains、activities 分别写入数据库
        mysql.write_dict(dict_info, table_name="ods_static_app_social_info_ft")
        df_tomysql(app_domain, 'ods_static_app_social_hosts_ft')
        df_tomysql(app_activitie, 'ods_static_app_social_activitie_ft')




#通过判断模块名运行上边函数
if __name__ == '__main__':
    path = r'E:\共享文件夹\app\汇总'
    API_KEY = 'd9debc714fc96cbeb1f987d2166c34946c470e1830dd9c7b67e7d6acbb1e7bb3'

    mysql = UseMysql('sibider', 'abc123!@#', 'test123')
    client = RemoteClient('192.168.10.134', 'speed', 'speed')
    # sftp_put(path)
    report_json(API_KEY)
