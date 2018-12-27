#!/usr/bin/evn python3
#coding=utf-8


import cv2
import numpy as np

'''
cv2 图像处理
'''


def output_img(img, file):
    cv2.imwrite(img, file)


def image_process(src_file, dest_file):
    '''
    图像处理
    :param filePath:
    :return:
    '''
    img = cv2.imread(src_file)

    # 降噪
    median_img = cv2.medianBlur(img, 3)
    output_img(r'D:\wangbin\my_workspace\selenium_test'
               r'\Pictures\median.png',
               median_img)

    # 灰度图
    gray_img = cv2.cvtColor(median_img,
                            cv2.COLOR_RGB2GRAY)
    output_img(r'D:\wangbin\my_workspace\selenium_test'
               r'\Pictures\gray.png',
               gray_img)

    # 直方图均衡化
    hist_img = cv2.equalizeHist(gray_img)
    output_img(r'D:\wangbin\my_workspace\selenium_test'
               r'\Pictures\hist.png',
               hist_img)

    # 二值化处理
    ret, binary_img = cv2.threshold(hist_img,
                                    140, 255,
                                    cv2.THRESH_BINARY)
    output_img(r'D:\wangbin\my_workspace\selenium_test'
               r'\Pictures\binary.png',
               binary_img)











def cv2_test():
    image_process(r'.\Pictures\jym.png',
            r'.\Pictures\a0.png')


    # median_blur(r'.\Pictures\jym.png',
    #             r'.\Pictures\a0.png')
    #
    # median_blur(r'.\Pictures\8460.bmp',
    #             r'.\Pictures\a1.png')
    #
    # median_blur(r'.\Pictures\1770.png',
    #             r'.\Pictures\a2.png')


if __name__=="__main__":
    cv2_test()

