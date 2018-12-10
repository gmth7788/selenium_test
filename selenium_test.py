#!/usr/bin/evn python3
#coding=utf-8



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def daka(browser, url=r"http://10.0.0.130"):
    browser.get(url)

    # user_name=browser.find_element_by_id("username")
    # pass_word=browser.find_element_by_id("password")
    # btn=browser.find_element_by_id("username")


    print(browser.page_source)
    # # 等待
    # wait = WebDriverWait(browser, 10)
    # wait.until(EC.presence_of_element_located((By.ID, "content_left")))


def test(browser, url=r"http://baidu.com"):
    #访问页面
    browser.get(url)


    # 查找元素
    # “百度一下”按钮
    baidu_btn = browser.find_element_by_id("su")

    # 输入框
    baidu_input = browser.find_element_by_id("kw")

    # 对获取到的元素调用交互方法
    baidu_input.send_keys("Python")
    baidu_btn.send_keys(Keys.ENTER)

    # 等待
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, "content_left")))

    pass



if __name__=="__main__":
    #声明浏览器对象
    browser = webdriver.Chrome()
    try:
        # test(browser)
        daka(browser)
        print("terminate successfully!")
    except Exception:
        print("failed.")
    finally:
        browser.close()


