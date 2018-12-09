#!/usr/bin/evn python3
#coding=utf-8


import requests
from bs4 import BeautifulSoup
import os
import sys

def send_mail():
    '''
    发送邮件
    :return:
    '''
    pass

def send_weixin():
    '''
    发送微信
    :return:
    '''
    pass

def send_weibo():
    '''
    发送微博
    :return:
    '''
    pass

def send_baidu_netdisk():
    '''
    发送百度网盘
    :return:
    '''
    pass




def download_with_RFBP(src_path, dest_path, total_size,
                       temp_size):
    '''
    断点续传(RFBP)
    从src_path偏移temp_size字节开始下载，添加到dest_path
    total_size源文件字节数
    temp_size已经下载的字节数
    '''
    headers = {'Range': 'bytes=%d-' % temp_size}
    r = requests.get(src_path, stream=True, verify=False,
                     headers=headers)
    with open(dest_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: 
                temp_size += len(chunk) 
                f.write(chunk) 
                f.flush() 
                ###这是下载实现进度显示#### 
                done = int(50 * temp_size / total_size) 
                sys.stdout.write("\r[%s%s] %d%%" %
                                 ('█' * done,
                                  ' ' * (50 - done),
                                  100 * temp_size /
                                  total_size))
                sys.stdout.flush() 
    print() # 避免上面\r 回车符


def download_file(src_path, dest_path, src_size):
    '''
    src_path，源文件路径
    dest_path，目标文件路径
    src_size, 源文件大小，若字典中没有"Content-Length"键值，该值有效。
    '''
    r = requests.get(src_path, stream=True)
    
    if os.path.exists(dest_path):
        tmp = os.path.getsize(dest_path)
    else: 
        tmp = 0

    if "Content-Length" in r.headers:
        total_size = int(r1.headers['Content-Length'])
    else:
        unit = ""
        src_size = src_size.upper()
        if src_size.find("KB") > 0:
            unit="KB"
            src_size = src_size.replace("KB","")
            total_size = float(src_size)
            temp_size = int(tmp/1024*100+0.5)/100
        elif src_size.find("MB") > 0:
            unit="MB"
            src_size = src_size.replace("MB","")
            total_size = float(src_size)
            temp_size = int(tmp/1024/1024*100+0.5)/100
        elif src_size.find("GB") > 0:
            unit="GB"
            src_size = src_size.replace("GB","")
            total_size = float(src_size)
            temp_size = int(tmp/1024/1024/1024*100+0.5)/100
        elif src_size.find("B") > 0:
            unit="B"
            src_size = src_size.replace("B","")
            total_size = int(src_size)
            temp_size = tmp
        else:
            print("源文件%s太大了。")
            return            

        print("src：{} {} {}".format(src_path,total_size,
                                    unit))
        print("dst: {} {} {}".format(dest_path, temp_size,
                                    unit))


    if (total_size > temp_size):
        download_with_RFBP(src_path, dest_path,
                           total_size, temp_size)


def lookup_html(root_link, page_url):
    '''
    root_link，下载文件的根路径
    page_url，页面URL
    '''
    src_path_list=[] #源文件路径
    src_size_list=[] #源文件大小
    dest_path_list=[] #目标文件路径
    r=requests.get(page_url)
    if r.status_code==200:
        soup=BeautifulSoup(r.text, 'lxml')
        index = 1
        for tr in soup.find_all('tr'):
            td_list = tr.find_all('td')
            a_list=tr.find_all('a')
            if a_list:
                src_path_list.append(root_link+'/'+
                                     a_list[0].get('href'))
                dest_path_list.append(
                    "../xikao/{}-{}.zip".format(
                        index, td_list[0].string))
                s = ""
                s = s.join(td_list[2].string)
                src_size_list.append(s)
                index+=1

    for (src_path,dest_path, src_size) in \
            zip(src_path_list, dest_path_list,
src_size_list):
        try:
            download_file(src_path, dest_path,
                          src_size)
            print("download OK.")
        except Exception as e:
            print('str(Exception):\t', str(Exception))
            print('str(e):\t\t', str(e))
            print('repr(e):\t', repr(e))
            print('traceback.print_exc():' +
                  traceback.print_exc())
            print('traceback.format_exc():\n%s' %
                  traceback.format_exc())
            print("download failed!")
        else:
            print("")


if __name__=="__main__":
    root_link="http://scripts.xikao.com"
    page_url="http://scripts.xikao.com/download"
    lookup_html(root_link, page_url)


