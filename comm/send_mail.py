#!/usr/bin/env python
# _*_ coding: utf-8 _*_

# 发邮件的模块

"""
auth: sunhaobo
version: 2.0
function: 邮件发送模块
usage:
note: 用法：
      1、定义subject, userlist, content
      2、调用sendmail(subject, userlist, content)，定义主体，收件人列表，内容
update: 1、函数封装成类，从配置文件中读取mail配置
        2、增加 html 的发送模块
date: 2022-12-05
"""

import smtplib
import sys
import base64
# from email import encoders
from email.header import Header  # 构造邮件头
from email.mime.text import MIMEText  # 构造邮件正文
from email.utils import parseaddr, formataddr
from comm.getconfig import get_config  # 引入配置文件

# rebuild目标，使用表格发送邮件

class MAIL:
    config = get_config()

    def __init__(self):
        self.config = self.config['mail']  # 读取 mail 字段
        self.smtp_user = self.config['smtp_user']  # 邮件名称可以使用 sunhaobpo@qianxin.com 中的 @ 切开来 str.split('@')[0]
        self.smtp_pass = self.config['smtp_pass']  # 发件人邮件密码
        self.smtp_host = self.config['smtp_host']  # 邮件服务器
        self.smtp_port = int(self.config['smtp_port'])  # 邮件端口

    def send_mail(self, subject, userlist, content):
        # 变量
        smtp_user = self.smtp_user
        smtp_pass = self.smtp_pass
        smtp_host = self.smtp_host
        smtp_port = self.smtp_port
        to_userlist = []
        # to_Addr = to_userlist
        to_Addr = userlist

        # 格式化头部【格式化一个邮件地址，不能简单的传入name，因为如果包含中文，需要通过Header对象进行编码】
        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr((Header(name, 'utf-8').encode(), addr))

        # 创建邮件对象 msg
        msg = MIMEText(content, 'plain', 'utf-8')  # content 邮件正文，plain 纯文本，utf-8 编码格式
        # msg = MIMEText(content, 'html', 'utf-8')
        # 发件人
        msg['From'] = _format_addr(smtp_user)

        # 收件人
        msg['To'] = _format_addr(';'.join(to_Addr))  # 使用[;]将收件人清单连接成一个字符串
        # Python join() 方法用于将序列中的元素以指定的字符连接生成一个新的字符串。str.join(sequence)

        # 邮件标题
        try:
            msg['Subject'] = Header(subject, 'utf-8').encode()  # 主题内容，使用 uft-8 编码保证兼容性
            smtp_server = smtplib.SMTP(smtp_host, smtp_port)
            smtp_server.starttls()
            smtp_server.set_debuglevel(0)
            smtp_server.login(smtp_user.split('@')[0], smtp_pass)  # 登录邮件服务器
            smtp_server.sendmail(smtp_user, to_Addr, msg.as_string())  # 邮件服务器发送邮件
            smtp_server.quit()  # 退出邮件服务器
        except Exception as e:
            print("Error:sand mail faild!")
            print(e)

    # 使用需要在内容里面定义html标签文本
    def send_mail_html(self, subject, userlist, contenthtml):
        # 变量
        smtp_user = self.smtp_user
        smtp_pass = self.smtp_pass
        smtp_host = self.smtp_host
        smtp_port = self.smtp_port
        to_userlist = []
        # to_Addr = to_userlist
        to_Addr = userlist

        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr((Header(name, 'utf-8').encode(), addr))

        # 创建邮件对象 msg
        # msg = MIMEText(content, 'plain', 'utf-8')  # content 邮件正文，plain 纯文本，utf-8 编码格式
        msg = MIMEText(contenthtml, 'html', 'utf-8')   # content 邮件正文 html格式，utf-8 编码格式
        # 发件人
        msg['From'] = _format_addr(smtp_user)

        # 收件人
        msg['To'] = _format_addr(';'.join(to_Addr))  # 使用[;]将收件人清单连接成一个字符串
        # Python join() 方法用于将序列中的元素以指定的字符连接生成一个新的字符串。str.join(sequence)

        # 邮件标题
        try:
            msg['Subject'] = Header(subject, 'utf-8').encode()  # 主题内容，使用 uft-8 编码保证兼容性
            smtp_server = smtplib.SMTP(smtp_host, smtp_port)
            smtp_server.starttls()
            smtp_server.set_debuglevel(0)
            smtp_server.login(smtp_user.split('@')[0], smtp_pass)  # 登录邮件服务器
            smtp_server.sendmail(smtp_user, to_Addr, msg.as_string())  # 邮件服务器发送邮件
            smtp_server.quit()  # 退出邮件服务器
        except Exception as e:
            print("Error:sand html mail faild!")
            print(e)


# 测试send_email函数
if __name__ == '__main__':
    Mail = MAIL()
    subject = 'Send Mail Test8'
    content = 'Mail Conten'
    contenthtml = '<h1>Mail Conten HTML</h1>'
    userlist = ['sunhaobo@qianxin.com']  # 收件人列表
    # Mail.send_mail(subject, userlist, content)
    Mail.send_mail_html(subject, userlist, contenthtml)
