#!/usr/bin/evn python3
#coding=utf-8

'''
百度云BCE，文字识别
'''

from aip import AipOcr



def get_file_content(filePath):
    """ 读取图片 """
    with open(filePath, 'rb') as fp:
        return fp.read()

def read_text(client, filePath):
    image = get_file_content(filePath)
    result = client.basicGeneral(image)
    print(result)
    ret_str = ""
    for i in range(result['words_result_num']):
        # print(result['words_result'][i]['words'])
        ret_str += result['words_result'][i]['words'] + "\n"
    print(ret_str)
    return ret_str

def read_number(client, filePath):
    '''
    读数字效果差强人意
    :param client:
    :param filePath:
    :return:
    '''
    image = get_file_content(filePath)
    result = client.numbers(image)
    print(result)
    ret_str = ""
    for i in range(result['words_result_num']):
        # print(result['words_result'][i]['words'])
        ret_str += result['words_result'][i]['words']
    print(ret_str)
    return ret_str





def aip_test():
   '''
   文本识别
   :return:
   '''
   APP_ID = '15144944'
   API_KEY = '9IF1gL9QKlWkI72KVW2F6gNi'
   SECRET_KEY = 'dOh8cCvKG17KNbB3snFeZwMpFSR7Hcep '

   client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

   # read_text(client, r'.\Pictures\11.png')
   # read_text(client, r'.\Pictures\12.png')
   # read_text(client, r'.\Pictures\bb.png')
   # read_number(client, r'.\Pictures\8460.bmp')
   # read_number(client, r'.\Pictures\1770.png')
   # read_number(client, r'.\Pictures\jym.png')

   read_number(client, r'.\Pictures\median.png')
   read_number(client, r'.\Pictures\gray.png')
   read_number(client, r'.\Pictures\hist.png')
   read_number(client, r'.\Pictures\binary.png')


if __name__=="__main__":
    aip_test()


