#!/usr/bin/evn python3
#coding=utf-8


'''
百度云BCE，文字识别
'''

from aip import AipOcr

import cv2
import numpy as np

import requests

from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import os

def get_file_content(filePath):
    """ 读取图片 """
    with open(filePath, 'rb') as fp:
        return fp.read()

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
    return ret_str

'''
OA打卡自动测试程序
'''

def daka(browser, url=r"http://10.0.0.130"):
    userid = "wang_bin"
    passwd = "wangbin"

    browser.get(url)

    # 选择OA页面
    browser.find_element(By.ID, "Button2").send_keys(
        Keys.ENTER)

    # 切换到新打开的页面
    browser.switch_to.window(browser.window_handles[1])
    print(browser.current_url)

    # 输入用户名和密码
    browser.find_element(By.ID, "username").send_keys(
        userid)
    browser.find_element(By.ID, "password").send_keys(
        passwd)
    time.sleep(1)
    browser.find_element(By.ID, "password").send_keys(
        Keys.ENTER)

    # 等待打开首页
    WebDriverWait(browser, 5, 0.5).until(
        EC.presence_of_element_located((By.ID,
                                        "DetailFrame"))
    )

    # 切换到目标表单
    browser.switch_to.frame("DetailFrame")

    # 进入“上下班登记”页面
    browser.find_element_by_xpath(
        "/ html / body / table[2] / tbody / tr[6]"
        " / td[1] / a[2]").send_keys(
        Keys.ENTER)


    # 等待打开“上下班登记”页面
    WebDriverWait(browser, 5, 0.5).until(
        EC.presence_of_element_located((By.ID,
                                        "CodeStr20090608"))
    )

    # 下载校验码图片文件
    image_element = browser.find_element_by_xpath(
        r'// *[ @ id = "frminfo"] / table[1] / tbody'
        r' / tr / td[2] / div / img')
    # 方法一：不能操控右键菜单，todo
    #ActionChains(browser).context_click(image_element).perform()
    # 方法二
    image_url = image_element.get_attribute("src")
    print(image_url)
    r = requests.get(image_url)
    with open(r'D:\wangbin\my_workspace\selenium_test'
              r'\Pictures\jym.png', "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(r"D:\wangbin\my_workspace"
                                   r"\selenium_test\Pictures"
                                   r"\screen_1.png")

    #################################
    # 图像处理
    img = cv2.imread(r'D:\wangbin\my_workspace\selenium_test'
                     r'\Pictures\jym.png')

    # 降噪
    median_img = cv2.medianBlur(img, 3)

    # 灰度图
    gray_img = cv2.cvtColor(median_img,
                            cv2.COLOR_RGB2GRAY)

    # 直方图均衡化
    hist_img = cv2.equalizeHist(gray_img)

    # 二值化处理
    ret, binary_img = cv2.threshold(hist_img,
                                    140, 255,
                                    cv2.THRESH_BINARY)
    cv2.imwrite(r'D:\wangbin\my_workspace\selenium_test'
                r'\Pictures\jym_0.png',
                binary_img)

    # 识别校验码
    APP_ID = '15144944'
    API_KEY = '9IF1gL9QKlWkI72KVW2F6gNi'
    SECRET_KEY = 'dOh8cCvKG17KNbB3snFeZwMpFSR7Hcep '

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    check_code = read_number(client,
                r'D:\wangbin\my_workspace\selenium_test'
                r'\Pictures\jym_0.png')
    print(check_code)

    # 执行js
    js = "window.scrollTo(100, 450)"
    browser.execute_script(js)

    time.sleep(10)
    print(browser.current_url)


if __name__=="__main__":
    #声明浏览器对象
    browser = webdriver.Chrome()
    try:
        # test(browser)
        daka(browser)
        print("terminate successfully!")
    except Exception as msg:
        print("failed.")
        print(msg)
    finally:
        browser.quit()


