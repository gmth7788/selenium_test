#!/usr/bin/evn python3
#coding=utf-8


'''
email test
'''

import os

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage




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
    image.add_header('Content_ID', '<image1')
    return image


def send_mail(info):
    '''
    发送邮件
    :return:
    '''
    send_user = 'bin_cn1@163.com'
    send_pwd = ''
    recv_user = 'orchard2046@163.com'

    msg = MIMEMultipart('mixed')
    msg['Subject'] = info
    msg['From'] = send_user
    msg['To'] = recv_user

    text_plain = get_text_plain("daka result")
    text_attach = get_attachment(r'./daka.log')
    text_image1 = get_image(r'./Pictures/tmp.png')
    text_image2 = get_image(r'./Pictures/jym.png')
    msg.attach(text_plain)
    msg.attach(text_attach)
    msg.attach(text_image1)
    msg.attach(text_image2)

    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com')
    smtp.login(send_user, send_pwd)
    smtp.sendmail(send_user, recv_user,
                  msg.as_string())
    smtp.quit()






if __name__=="__main__":
    send_mail('daka result')





