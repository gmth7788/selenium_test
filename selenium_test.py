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

def jym_proc(image_element, path, filename):
    '''
    校验码处理
    :return:
    '''
    # 方法一：不能操控右键菜单，todo
    #ActionChains(browser).context_click(image_element).perform()
    # 方法二
    image_url = image_element.get_attribute("src")
    print(image_url)
    r = requests.get(image_url)
    with open(path+filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(path+"\screen_1.png")

def image_process(path, filename, proc_filename):
    '''
    图像处理
    :param path:
    :param filename:
    :param proc_filename:
    :return:
    '''
    #################################
    # 图像处理
    img = cv2.imread(path+filename)

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
    cv2.imwrite(path+proc_filename, binary_img)

def image_recognition(path, proc_filename):
    '''
    图像识别
    :param path:
    :param proc_filename:
    :return:
    '''
    APP_ID = '15144944'
    API_KEY = '9IF1gL9QKlWkI72KVW2F6gNi'
    SECRET_KEY = 'dOh8cCvKG17KNbB3snFeZwMpFSR7Hcep '

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    check_code = read_number(client, path+proc_filename)
    return check_code


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

    # 处理校验码
    path = r'D:\wangbin\my_workspace\selenium_test\Pictures'
    filename = r'\jym.png'
    proc_filename = r'\jym_0.png'
    for i in range(10):
        # 下载校验码图片文件
        image_element = browser.find_element_by_xpath(
            r'// *[ @ id = "frminfo"] / table[1] / tbody'
            r' / tr / td[2] / div / img')
        jym_proc(image_element, path, filename)

        # 图像处理
        image_process(path, filename, proc_filename)

        # 图像识别
        check_code = image_recognition(path, proc_filename)
        print(check_code)
        if len(check_code) == 4:
            print("ok. jym="+check_code)
            break
        else:
            print("failed. try again.")

    # 输入验证码
    jym_input_element = browser.find_element_by_xpath(
        r'// *[ @ id = "CodeStr20090608"]')
    jym_input_element.send_keys(check_code)

    # 上班/下班登记
    jym_input_element = browser.find_element_by_xpath(
        r'// *[ @ id = "frminfo"] / table[2] / tbody / tr[3] / td[4] / a')
    jym_input_element.send_keys(Keys.ENTER)

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


