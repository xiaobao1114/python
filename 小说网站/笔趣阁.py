import requests
import re


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

if __name__ == '__main__':
    #main_url是小说首页地址，切换成你想要爬的小说网页
    main_url = 'https://www.biquge11.cc/read/12972/'
    #发送请求
    mainText = requests.get(main_url, headers = headers).text
    info_lists = re.findall('<dd><a href ="(.*?)">(.*?)</a></dd>',mainText)
    for info in info_lists:
        url = 'https://www.biquge11.cc' +  info[0]
        print(url)
        #获取数据
        response = requests.get(url)
        html_data = response.text

        #解析数据
        content = re.findall('class="Readarea ReadAjax_content">(.*?)<br /><br />',html_data)[0]
        #替换换行符
        text ='\n\n' + info[1] + '\n\n'
        text+= content.replace("<br /><br />", '\n')
        print("正在获取" + info[1] + url)
        #保存到文件
        f = open('斗破苍穹.txt',mode='a',encoding='utf-8')
        f.write(text)
