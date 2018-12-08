#!/usr/bin/evn python3
#coding=utf-8


import requests
from bs4 import BeautifulSoup


def download_file1(src_path, dest_path):
    r = requests.get(src_path, stream=True)
    with open(dest_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()



def lookup_html(root_link, download_link):
    r=requests.get(download_link)
    if r.status_code==200:
        soup=BeautifulSoup(r.text)
        index = 1
        for tr in soup.find_all('tr'):
            td_list = tr.find_all('td')
            a_list=tr.find_all('a')
            if a_list:
                src_path=root_link+'/'+a_list[0].get('href')
                dest_path="../xikao/{}-{}.zip".format(
index, td_list[0].string) #目标文件路径
                print("downloading: "+src_path+" -> "+dest_path)
                download_file1(src_path, dest_path)
                index+=1
    print("terminate normally.")    



def download_file(url, index):
    local_filename = index+"-"+url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


if __name__=="__main__":
    root_link="http://scripts.xikao.com"
    download_link="http://scripts.xikao.com/download"
    lookup_html(root_link, download_link)

'''
    r=requests.get(root_link)
    if r.status_code==200:
        soup=BeautifulSoup(r.text)
        # print soup.prettify()
        index=1
        for link in soup.find_all('a'):
            new_link=root_link+link.get('href')
            if new_link.endswith(".zip"):
                file_path=download_file(new_link,str(index))
                print("downloading:"+new_link+" -> "+file_path)
                index+=1
                print("all download finished")
            else:
                print("errors occur.")
'''


