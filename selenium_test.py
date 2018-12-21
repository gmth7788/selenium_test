#!/usr/bin/evn python3
#coding=utf-8


'''
百度云BCE，文字识别
'''
from aip import AipOcr

from PIL import Image

import win32api
import win32con
import win32gui

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

def get_file_content(file_name):
    '''
    读取文件内容
    :param file_name:
    :return: 返回二进制文件
    '''
    with open(file_name, 'rb') as fp:
        return fp.read()

def read_number(aip_ocr, file_name):
    '''
    读数字效果差强人意
    :param aip_ocr: 百度OCR
    :param file_name: 文件名
    :return:
    '''
    image = get_file_content(file_name)
    result = aip_ocr.numbers(image)
    print(result)
    ret_str = ""
    for i in range(result['words_result_num']):
        # print(result['words_result'][i]['words'])
        ret_str += result['words_result'][i]['words']
    return ret_str

def jym_proc_3(browser, image_element, file_name):
    '''
    校验码处理，方法三，截取页面快照中的校验码
    1）截屏为临时文件".\tmp.png"；
    2）截取校验码图片，截屏图像分辨率太低，只做降噪处理。
    :param browser: 浏览器对象
    :param image_element: 校验码对象
    :param file_name: 校验码文件名
    :return:
    '''
    print("校验码处理，方法三")

    root_path = os.path.dirname(file_name)

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(root_path+r"\tmp.png")

    # 获取验证码的x，y轴
    location = image_element.location
    print(location)
    location['x'] = 1995
    location['y'] = 87

    # 获取验证码的长和宽
    size = image_element.size
    # 需要截取的验证码坐标
    rect_range = (
        int(location['x']), int(location['y']),
        int(location['x']) + size['width'],
        int(location['y']) + size['height'])
    print(rect_range)

    img = Image.open(root_path+r"\tmp.png")
    checkcode_img = img.crop(rect_range)
    checkcode_img.save(file_name)


def jym_proc_1(browser, image_element, root_path, file_name):
    '''
    校验码处理，方法一
    :return:
    '''
    # 删除“C:\Users\lenovo\Downloads\Kq_GetCode.asp”
    cmd_str = r"del /F C:\Users\lenovo\Downloads\Kq_GetCode.asp"
    ret = os.popen(cmd_str)
    print("删除图片(%s)" % ret)

    # 右键弹出菜单
    ActionChains(browser).context_click(image_element).perform()
    win32api.keybd_event(40,0,0,0)  # DOWN ARROW
    win32api.keybd_event(40,0,0,0)  # DOWN ARROW
    win32api.keybd_event(13,0,0,0)  # ENTER
    # win32api.keybd_event(40,0,KEYEVENT_KEYUP,0)

    # 弹出另存为对话框
    # 获取句柄
    # classname = "#32770"
    # titlename = "另存为"
    # hwnd = win32gui.FindWindow(classname, titlename)
    # hwnd = win32gui.FindWindowEx(
    #     0, 0, "Button", "保存(&S)")
    hwnd = win32gui.FindWindow(0, u"另存为")
    if hwnd:
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN,
                             win32con.VK_RETURN, 0)
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP,
                             win32con.VK_RETURN, 0)
    else:
        print("can't found window.")

    # 另存图片
    # 将“C:\Users\lenovo\Downloads\Kq_GetCode.asp”
    # 另存为“D:\wangbin\my_workspace\selenium_test\Pictures\jym.png”
    cmd_str = r"copy /Y C:\Users\lenovo\Downloads\Kq_GetCode.asp " \
              r"D:\wangbin\my_workspace\selenium_test\Pictures\jym.png "
    ret = os.popen(cmd_str)
    print("另存图片(%s)" % ret)

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(root_path+"\screen_1.png")
    print("校验码处理，方法一")


def jym_proc_2(browser, image_element, root_path, file_name):
    '''
    校验码处理，方法二
    :return:
    '''
    image_url = image_element.get_attribute("src")
    print(image_url)
    r = requests.get(image_url)
    with open(root_path+file_name, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(root_path+"\screen_1.png")

def image_process(input_file, output_file):
    '''
    图像处理
    :param input_file: 输入文件名
    :param output_file: 输出文件名
    :return:
    '''
    root_path = os.path.dirname(output_file)

    #################################
    # 图像处理
    img = cv2.imread(input_file)

    # 降噪
    median_img = cv2.medianBlur(img, 3)
    cv2.imwrite(root_path + r"\median_img.png", median_img)

    # 灰度图
    gray_img = cv2.cvtColor(median_img,
                            cv2.COLOR_RGB2GRAY)
    cv2.imwrite(root_path + r"\gray_img.png", gray_img)

    # 直方图均衡化
    hist_img = cv2.equalizeHist(gray_img)
    cv2.imwrite(root_path + r"\hist_img.png", hist_img)

    # 二值化处理
    # ret, binary_img = cv2.threshold(
    #     hist_img, 140, 255, cv2.THRESH_BINARY)
    # cv2.imwrite(root_path + r"\binary_img", binary_img)

    # 配合方法三，以灰度图输出
    cv2.imwrite(output_file, gray_img)


def image_recognition(file_name):
    '''
    图像识别
    :param file_name: 文件名
    :return: 返回校验码字符串
    '''
    APP_ID = '15144944'
    API_KEY = '9IF1gL9QKlWkI72KVW2F6gNi'
    SECRET_KEY = 'dOh8cCvKG17KNbB3snFeZwMpFSR7Hcep '

    aip_ocr = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    check_code = read_number(aip_ocr, file_name)
    return check_code


def login_oa(browser, url):
    '''
    登录到OA
    :param browser: 浏览器对象
    :url: OA地址
    :return:
    '''
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
    print(browser.current_url)

def refresh_oa(browser):
    '''
    刷新OA首页
    :param browser: 浏览器对象
    :return:
    '''
    # 刷新当前页面
    browser.refresh()

    # 切换到目标表单
    browser.switch_to.frame("DetailFrame")

    # 进入“上下班登记”页面
    browser.find_element_by_xpath(
        "/ html / body / table[2] / tbody / tr[6]"
        " / td[1] / a[2]").send_keys(Keys.ENTER)

    # 等待打开“上下班登记”页面
    WebDriverWait(browser, 5, 0.5).until(
        EC.presence_of_element_located(
            (By.ID, "CodeStr20090608")))

    print(browser.current_url)


def get_jym(browser):
    '''
    获取校验码
    :param browser: 浏览器对象
    :return: 成功返回(0, 校验码字符串)，否则返回(-1, '')
    '''
    root_path = r'D:\wangbin\my_workspace\selenium_test\Pictures'
    jym_filename = r'\jym.png'
    jym0_filename = r'\jym_0.png'

    for i in range(10):
        # 下载校验码图片文件
        image_element = browser.find_element_by_xpath(
            r'// *[ @ id = "frminfo"] / table[1] / tbody'
            r' / tr / td[2] / div / img')
        # jym_proc_2(browser, image_element, root_path, jym_filename)
        # jym_proc_1(browser, image_element, root_path, jym_filename)
        jym_proc_3(browser, image_element, root_path+jym_filename)

        # 图像处理
        image_process(root_path+jym_filename,
                      root_path+jym0_filename)

        # 图像识别
        check_code = image_recognition(root_path+jym0_filename)
        if len(check_code) == 4:
            ret = 0
            print("ok. jym="+check_code)
            break
        else:
            ret = -1
            check_code = ''
            print("failed. try again.")
            refresh_oa(browser)

    return ((ret, check_code))

def daka(browser, url=r"http://10.0.0.130"):
    '''
    OA打卡自动测试程序
    :param browser: 浏览器对象
    :param url: 默认OA打卡URL
    :return: 成功返回0
    '''
    # 登录到OA
    login_oa(browser, url)

    # 刷新OA首页
    refresh_oa(browser)

    # 获取校验码
    (ret, check_code) = get_jym(browser)
    if ret != 0:
        print("获取校验码失败！")
        return ret
    else:
        print("获取校验码成功。")

    # 输入验证码
    jym_input_element = browser.find_element_by_xpath(
        r'// *[ @ id = "CodeStr20090608"]')
    jym_input_element.send_keys(check_code)

    # 上班/下班登记
    # 上班登记
    login_jym_input_element = browser.find_element_by_xpath(
        r'//*[@id="frminfo"]/table[2]/tbody/tr[2]/td[4]/a')
    login_jym_input_element.send_keys(Keys.ENTER)

    # 下班登记
    logout_jym_input_element = browser.find_element_by_xpath(
        r'//*[@id="frminfo"]/table[2]/tbody/tr[3]/td[4]/a')
    logout_jym_input_element.send_keys(Keys.ENTER)

    # 确认对话框
    # browser.switch_to_alert().accept()

    # 执行js
    js = "window.scrollTo(100, 450)"
    browser.execute_script(js)

    time.sleep(2)

    return ret



if __name__=="__main__":
    browser = webdriver.Chrome()
    try:
        if 0 == daka(browser):
            print("打卡成功。")
        else:
            print("打卡失败！")
    except Exception as msg:
        print("failed.")
        print(msg)
    finally:
        browser.quit()


