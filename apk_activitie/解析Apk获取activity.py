import os
import shutil
import subprocess
import re
import pymysql
from datetime import datetime, date, time


# 使用apktool解码APK文件
def decode_apk(apk_path, output_dir):
    apktool_path = r'apktool_2.9.3\apktool.bat'
    cmd = [apktool_path, 'd', apk_path, '-o', output_dir]
    input_data = 'ads'
    # print(apktool_path,cmd,input_data)
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=input_data.encode())
        # print(stdout,stderr)
        print(f"2.{apk_path}解码成功")
    except Exception as e:
        print(f"Error decoding APK：{e}")

    # 解析解码后的APK目录中的AndroidManifest.xml文件


def get_app_activities(decoded_apk_dir):
    manifest_path = os.path.join(decoded_apk_dir, 'AndroidManifest.xml')
    print('3.解析 ' + manifest_path)
    try:
        with open(r'%s' % manifest_path, 'r', errors='ignore') as f:
            content = f.read()
            # print(content)
            person_pattern_package = 'package="(.+?)"'
            person_pattern_android = 'android:name="(.*?)"'
            package_name = re.findall(person_pattern_package, content, re.S)
            android_name = re.findall(person_pattern_android, content, re.S)
            return package_name, android_name
    except Exception as e:
        print(f"3.Error parsing manifest：{e}")
        return []

    # 清理解码后的APK目录


def clean_up(output_dir):
    try:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    except Exception as e:
        print(f"删除文件：Error  {e}")
    # 写入文件名，包名，android_name


def open_write(apk_name, package_name, activities, wc):
    wc.write("apk_name, package_name, android_name \n")
    print('  %s 写入csv' % apk_name)
    for android_name in activities[1]:
        wc.write("{}, {}, {} \n".format(apk_name, package_name, android_name))


def insert_sql(apk_name, package_name, activities):
    # 数据库连接信息
    db = pymysql.connect(
        host='192.168.10.102',
        user='root',
        passwd='123456',
        db='speed',
        port=3306,
        charset="utf8"
    )
    # -*- coding:utf-8 -*-
    try:
        cursor = db.cursor()
        create_sql = 'create table if not exists ods_speed_apk_activitie (apk_name varchar(120),package_name varchar(120),android_name varchar(120),date_id varchar(120)) default charset=utf8 '
        cursor.execute(create_sql)
        today = date.today().strftime("%Y%m%d")
        print('4.写入数据库')
        for android_name in activities[1]:
            sql = 'insert into ods_speed_apk_activitie values(%s,%s,%s,%s)'
            # print(apk_name,package_name,android_name)
            list = [apk_name, package_name, android_name, today]
            # 列表传参
            cursor.execute(sql, list)
        db.commit()
    except Exception as e:
        print(f'{apk_name}写入数据库失败'.format(apk_name))
    cursor.close()
    db.close()


def file_size(csv_path):
    file_size = os.path.getsize(csv_path)
    print(f'  {csv_path} 文件大小为: {file_size} 字节')


def apk_activities(apk_dir):
    print('开始时间：%s' % datetime.now())
    apk_files = [os.path.join(apk_dir, f) for f in os.listdir(apk_dir) if f.endswith('.apk')]
    # 遍历APK文件列表并解码
    for apk_path in apk_files:
        try:
            apk_name = os.path.basename(apk_path).replace('.apk', '')
            csv_path = apk_path.replace('.apk', '.csv')
            wc = open('%s' % csv_path, 'w')
            print(f'\n1.创建 {apk_name} csv文件')
            # 生成唯一的输出目录名，避免冲突
            output_dir = os.path.join(output_base_dir, os.path.splitext(os.path.basename(apk_path))[0])
            decode_apk(apk_path, output_dir)
            activities = get_app_activities(output_dir)
            # 判断是否获取到Activity信息
            if activities:
                print(f"4.Activities  {os.path.basename(apk_path)}")
                package_name = "".join(activities[0])
                # 写入文件
                open_write(apk_name, package_name, activities, wc)
                # insert_sql(apk_name, package_name, activities)
                file_size(csv_path)
                # 清理解码目录（可选）
                clean_up(output_dir)
            else:
                print(f"4.No activities found for {os.path.basename(apk_path)}")
        except Exception as e:
            print("There was a problem: ", str(e))
            continue
    print('结束时间：%s' % datetime.now())


if __name__ == '__main__':
    # APK文件所在的目录E:\共享文件夹\app\downkuai
    apk_dir = r'E:\共享文件夹\app\快手活跃APK\2024年5月24日'
    # 解码后的APK文件存放基础目录
    output_base_dir = r'/apk_activitie\\apk'
    # 获取APK文件列表

    apk_activities(apk_dir)

