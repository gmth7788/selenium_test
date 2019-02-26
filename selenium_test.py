#!/usr/bin/evn python3
#coding=utf-8


'''
百度云BCE，文字识别
'''
from aip import AipOcr

import configparser
import pyautogui

import win32api
import win32con
import win32gui

import cv2
import numpy as np
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import requests

import time
import datetime
import os
import re
import traceback
import logging

LOG_FILE = r'./daka.log'
IMAGE_FILE = r'./Pictures/result.png'
TMP_IMAGE_FILE = r'./Pictures/tmp.png'
JYM_IMAGE_FILE = r'./Pictures/jym.png'

DAKA_CONFIG_FILE = r"./daka.ini"

class daka_config:
    '''
    daka配置
    '''

    def __init__(self):
        if os.path.exists(DAKA_CONFIG_FILE):
            self.get_config(DAKA_CONFIG_FILE)
        else:
            log("读取配置文件[%s]失败。" % DAKA_CONFIG_FILE)

    def get_config(self, cfg_file):
        '''
        读取配置文件
        :param cfg_file: 配置文件名
        :return:
        '''
        config = configparser.ConfigParser()
        config.read(cfg_file)
        sections = config.sections()

        self.userid = config['USER']['userid']
        self.passwd = config['USER']['passwd']

        self.root_path = config['COMMON']['root_path']
        self.image_path = self.root_path + '\\' + 'Pictures'
        self.log_file = config['COMMON']['log_file']
        self.image_file = config['COMMON']['image_file']
        self.tmp_image_file = config['COMMON']['tmp_image_file']
        self.jym_image_file = config['COMMON']['jym_image_file']

        self.smtp_server = config['MAIL']['smtp_server']
        self.send_user = config['MAIL']['send_user']
        self.send_pwd = config['MAIL']['send_pwd']
        self.recv_user = config['MAIL']['recv_user']
        self.subject = config['MAIL']['subject']

        self.baidu_app_id = config['BAIDU_APP']['APP_ID']
        self.baidu_api_key = config['BAIDU_APP']['API_KEY']
        self.baidu_secret_key = config['BAIDU_APP']['SECRET_KEY']


def pyautogui_set():
    '''
    PyAutoGUI设置
    :return:
    '''
    # 把鼠标光标在屏幕左上角，PyAutoGUI函数就会产生
    # pyautogui.FailSafeException异常，这样就能
    # 终止PyAutoGUI执行。
    # 上线版本要设置为False
    pyautogui.FAILSAFE = False

    # 所有的PyAutoGUI函数增加延迟，2.5秒
    pyautogui.PAUSE = 1.0

def get_attachment(file):
    '''
    添加附件
    :param file: 附件文件名
    :return: 返回附件
    '''
    name = os.path.basename(file)
    sendfile = open(file, 'rb').read()
    text_att = MIMEText(sendfile, 'base64', 'utf-8')
    text_att["Content-Type"] = 'application/octet-stream'
    text_att["Content-Disposition"] = \
        'attachment; filename="{}"'.format(name)
    return text_att

def get_text_plain(info):
    '''
    添加普通文本
    :param info:
    :return: 返回普通文本
    '''
    text_plain = MIMEText(info, 'plain', 'utf-8')
    return text_plain

def get_image(file):
    '''
    添加图片
    :param file:
    :return: 返回MIMEImage
    '''
    sendfile = open(file, 'rb').read()
    image = MIMEImage(sendfile)
    image.add_header('Content_ID', '<image1>')
    return image


def send_mail(info, flag):
    '''
    发送邮件
    :return:
    '''
    cfg = daka_config()
    smtp_server = cfg.smtp_server
    send_user = cfg.send_user
    send_pwd = cfg.send_pwd
    recv_user = cfg.recv_user

    msg = MIMEMultipart('mixed')
    msg['Subject'] = cfg.subject
    msg['From'] = send_user
    msg['To'] = recv_user

    text_plain = get_text_plain(info)
    text_attach = get_attachment(LOG_FILE)
    if "OK" == flag:
        text_image1 = get_image(IMAGE_FILE)
    else:
        text_image1 = get_image(TMP_IMAGE_FILE)
    text_image2 = get_image(JYM_IMAGE_FILE)
    msg.attach(text_plain)
    msg.attach(text_attach)
    msg.attach(text_image1)
    msg.attach(text_image2)

    smtp = smtplib.SMTP()
    smtp.connect(smtp_server)
    smtp.login(send_user, send_pwd)
    smtp.sendmail(send_user, recv_user,
                  msg.as_string())
    smtp.quit()

def log(msg):
    '''
    错误输出
    :param msg: 消息信息
    :return:
    '''
    print(msg)
    logging.info(msg)

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
    log(result)
    ret_str = ""
    for i in range(result['words_result_num']):
        # log(result['words_result'][i]['words'])
        ret_str += result['words_result'][i]['words']
    return ret_str


def jym_proc_4(browser, image_element, file_name):
    '''
    校验码处理，方法四
    使用pyAutoGUI完成界面操作
    :param browser:
    :param image_element:
    :param file_name:
    :return:
    '''
    log("校验码处理，方法四")

    # 鼠标移到屏幕中央
    screenWidth, screenHeight = pyautogui.size()
    pyautogui.moveTo(screenWidth / 2, screenHeight / 2)

    root_path = os.path.dirname(file_name)

    # 右键弹出菜单
    ActionChains(browser).context_click(image_element).perform()
    pyautogui.press("down")
    pyautogui.press("down")
    pyautogui.press("enter")
    # win32api.keybd_event(40, 0, 0, 0)  # DOWN ARROW
    # win32api.keybd_event(40, 0, 0, 0)  # DOWN ARROW
    # win32api.keybd_event(13, 0, 0, 0)  # ENTER

    # 弹出“另存为”对话框
    pyautogui.typewrite(file_name)
    pyautogui.press("enter")
    pyautogui.press("tab")
    pyautogui.press("enter")

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(r"%s\screen_1.png" %
                                   root_path)



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
    log("校验码处理，方法三")

    root_path = os.path.dirname(file_name)

    # 获取验证码的x，y轴
    location = image_element.location
    log(location)
    location['x'] = 1995
    location['y'] = 87

    # 获取验证码的长和宽
    size = image_element.size
    # 需要截取的验证码坐标
    rect_range = (
        int(location['x']), int(location['y']),
        int(location['x']) + size['width'],
        int(location['y']) + size['height'])
    log(rect_range)

    img = Image.open(root_path+r"\tmp.png")
    checkcode_img = img.crop(rect_range)
    checkcode_img.save(file_name)

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(r"%s\screen_1.png" %
                                   root_path)


def jym_proc_2(browser, image_element, file_name):
    '''
    校验码处理，方法二
    再次发起request后，返回的验证码就不是本次会话的验证码了，
    这个方法不行。
    :return:
    '''
    log("校验码处理，方法二")

    root_path = os.path.dirname(file_name)

    image_url = image_element.get_attribute("src")
    log(image_url)
    r = requests.get(image_url)
    with open(root_path+file_name, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(r"%s\screen_1.png" %
                                   root_path)


def jym_proc_1(browser, image_element, root_path, file_name):
    '''
    校验码处理，方法一，丢弃不用
    :return:
    '''
    # 删除“C:\Users\lenovo\Downloads\Kq_GetCode.asp”
    cmd_str = r"del /F C:\Users\lenovo\Downloads\Kq_GetCode.asp"
    ret = os.popen(cmd_str)
    log("删除图片(%s)" % ret)

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
        log("can't found window.")

    # 另存图片
    cmd_str = r"copy /Y C:\Users\lenovo\Downloads\Kq_GetCode.asp " \
              r".\Pictures\jym.png "
    ret = os.popen(cmd_str)
    log("另存图片(%s)" % ret)

    # 截取当前窗口，并制定保存位置
    browser.get_screenshot_as_file(root_path+"\screen_1.png")
    log("校验码处理，方法一")



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
    cv2.imwrite(root_path + "\\" + r"median_img.png", median_img)

    # 灰度图
    gray_img = cv2.cvtColor(median_img,
                            cv2.COLOR_RGB2GRAY)
    cv2.imwrite(root_path + "\\" + r"gray_img.png", gray_img)

    # 直方图均衡化
    hist_img = cv2.equalizeHist(gray_img)
    cv2.imwrite(root_path + "\\" + r"hist_img.png", hist_img)

    # 二值化处理
    # ret, binary_img = cv2.threshold(
    #     hist_img, 140, 255, cv2.THRESH_BINARY)
    # cv2.imwrite(root_path + r"\binary_img", binary_img)

    # 配合方法三，以灰度图输出
    cv2.imwrite(output_file, gray_img)


def image_recognition(file_name):
    '''
    百度图像识别
    :param file_name: 文件名
    :return: 返回校验码字符串
    '''
    cfg = daka_config()

    aip_ocr = AipOcr(cfg.baidu_app_id,
                     cfg.baidu_api_key,
                     cfg.baidu_secret_key)

    check_code = read_number(aip_ocr, file_name)
    return check_code


def login_oa(browser, url):
    '''
    登录到OA
    :param browser: 浏览器对象
    :url: OA地址
    :return:
    '''
    cfg = daka_config()

    browser.get(url)

    # 选择OA页面
    browser.find_element(By.ID, "Button2").send_keys(
        Keys.ENTER)

    # 切换到新打开的页面
    browser.switch_to.window(browser.window_handles[1])
    log(browser.current_url)

    # 输入用户名和密码
    browser.find_element(By.ID, "username").send_keys(
        cfg.userid)
    browser.find_element(By.ID, "password").send_keys(
        cfg.passwd)
    time.sleep(1)
    browser.find_element(By.ID, "password").send_keys(
        Keys.ENTER)

    # 等待打开首页
    WebDriverWait(browser, 5, 0.5).until(
        EC.presence_of_element_located((By.ID,
                                        "DetailFrame"))
    )
    log(browser.current_url)

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

    log(browser.current_url)


def get_jym(browser):
    '''
    获取校验码
    :param browser: 浏览器对象
    :return: 成功返回(0, 校验码字符串)，否则返回(-1, '')
    '''
    cfg = daka_config()

    # 创建image_path
    try:
        os.mkdir(cfg.image_path)
    except:
        pass

    # 下载校验码图片文件
    image_element = browser.find_element_by_xpath(
        r'// *[ @ id = "frminfo"] / table[1] / tbody'
        r' / tr / td[2] / div / img')
    # jym_proc_2(browser, image_element, root_path, jym_filename)
    # jym_proc_1(browser, image_element, root_path, jym_filename)
    # jym_proc_3(browser, image_element, root_path+jym_filename)
    jym_proc_4(browser, image_element,
               cfg.image_path + '\\' + cfg.jym_image_file)

    # 图像处理
    image_process(cfg.image_path + '\\' + cfg.jym_image_file,
                  cfg.image_path + '\\' + "tmp.png")

    # 图像识别
    check_code = image_recognition(cfg.image_path + '\\' + "tmp.png")
    if len(check_code) == 4:
        ret = 0
        log("ok. jym="+check_code)
    else:
        ret = -1
        check_code = ''

    return ((ret, check_code))

def my_login(browser):
    '''
    上班登记
    :param browser:
    :return: 成功返回0
    '''
    ret = 0
    try:
        login_jym_input_element = browser.find_element_by_xpath(
            r'//*[@id="frminfo"]/table[2]/tbody/tr[2]/td[4]/a')
        login_jym_input_element.send_keys(Keys.ENTER)
    except NoSuchElementException as msg:
        # 未发现上班登记链接，已经打卡
        ret = 100
    return ret


def my_logout(browser):
    '''
    下班登记
    :param browser:
    :return: 成功返回0
    '''
    ret = 0
    try:
        logout_jym_input_element = browser.find_element_by_xpath(
            r'//*[@id="frminfo"]/table[2]/tbody/tr[3]/td[4]/a')
        logout_jym_input_element.send_keys(Keys.ENTER)
    except NoSuchElementException as msg:
        # 未发现下班登记链接，已经打卡
        ret = 100
    return ret


def get_exp_logout_time(browser):
    '''
    获得应当下班时间
    :param browser:
    :return: 返回datetime类型
    '''
    ydxbsj = browser.find_element_by_xpath(
        r'//*[@id="frminfo"]/table[3]/tbody/tr/td[2]/font')
    log(ydxbsj.text)
    l = re.findall(r'(\d+)\:(\d+):(\d+)', ydxbsj.text)
    t = tuple(l[0])
    n = datetime.datetime.now()
    t0 = datetime.datetime(n.year, n.month, n.day,
                           int(t[0]), int(t[1]), int(t[2]))
    log(t0)
    return t0

def daka(browser, url=r"http://10.0.0.130"):
    '''
    OA打卡自动测试程序
    :param browser: 浏览器对象
    :param url: 默认OA打卡URL
    :return: 成功返回0
    '''
    # 登录到OA
    login_oa(browser, url)

    ret = -1
    for i in range(100):

        # 刷新OA首页
        refresh_oa(browser)

        # 获取校验码
        (ret, check_code) = get_jym(browser)
        if ret != 0:
            log("获取校验码失败！")
            continue
        else:
            log("获取校验码成功。")

        # 输入验证码
        jym_input_element = browser.find_element_by_xpath(
            r'// *[ @ id = "CodeStr20090608"]')
        jym_input_element.send_keys(check_code)

        # 上班/下班登记
        # 获取当前时间
        now_time = datetime.datetime.now()
        if now_time.hour < 10:
            # 上午10点前，尝试上班登记
            ret = my_login(browser)
        else:
            # 获取应当下班时间
            t0 = get_exp_logout_time(browser)
            t0 = t0 + datetime.timedelta(minutes=5)  # 向后推迟5分钟
            log(t0)
            if now_time > t0:
                # 尝试下班登记
                ret = my_logout(browser)

        # 截取当前窗口，并制定保存位置
        browser.get_screenshot_as_file(IMAGE_FILE)

        if ret != 100:
            continue
        else:
            ret = 0
            break

        # try:
        #     # 校验码不正确对话框
        #     alert = browser.switch_to.alert()
        #     print("弹出对话框:" + alert.text)
        #     if alert.text == "校验码不正确！":
        #         log("校验码不正确，重新打卡。")
        #         browser.switch_to_alert().accept()
        # except NoAlertPresentException as msg:
        #     # 校验码通过校验，退出循环
        #     if 0 == ret:
        #         # 截取当前窗口，并制定保存位置
        #         browser.get_screenshot_as_file(IMAGE_FILE)
        #         break
        # except (TypeError, Exception) as e:
        #     log('str(Exception):\t' + str(Exception))
        #     log('str(e):\t\t' + str(e))
        #     log('repr(e):\t' + repr(e))
        #     log('traceback.print_exc():')
        #     log(traceback.print_exc())
        #     log('traceback.format_exc():\n')
        #     log(traceback.format_exc())
        #     continue

    # # 执行js
    # js = "window.scrollTo(100, 450)"
    # browser.execute_script(js)
    #
    # time.sleep(2)

    return ret



if __name__=="__main__":
    cfg = daka_config()

    pyautogui_set()

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=cfg.log_file,
                        level=logging.INFO,
                        format=LOG_FORMAT)

    browser = webdriver.Chrome()
    try:
        ret = daka(browser)
        if 0 == ret:
            log("打卡成功。")
            send_mail("打卡成功", "OK")
        else:
            send_mail("打卡失败", "FAILED")
            log("打卡失败！({})".format(ret))
    except Exception as e:
        log('str(Exception):\t'+str(Exception))
        log('str(e):\t\t'+str(e))
        log('repr(e):\t'+repr(e))
        log('traceback.print_exc():')
        log(traceback.print_exc())
        log('traceback.format_exc():\n')
        log(traceback.format_exc())
    finally:
        browser.quit()


