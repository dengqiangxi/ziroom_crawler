#!/usr/bin/env python
# -*- coding=utf8 -*-
# Created by dengqiangxi at 2018/4/10
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configurations import mail_config


# 发送邮件
def sendmail(subject, message=u'请及时查收，谢谢。'):
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sender = mail_config['sender']
    receiver = mail_config['receiver']
    smtpserver = mail_config['smtpserver']
    smtpport = mail_config['smtpport']
    password = mail_config['password']
    subject = u'房源提醒-' + subject
    # 下面的to\cc\from最好写上，不然只在sendmail中，可以发送成功，但看不到发件人、收件人信息
    msgroot = MIMEMultipart('related')
    msgroot['Subject'] = subject
    msgroot['From'] = sender
    msgroot['To'] = receiver

    # MIMEText有三个参数，第一个对应文本内容，第二个对应文本的格式，第三个对应文本编码
    message = MIMEText(u' {}\n\n\n {}\n\n made by dengqiangxi'.format(message,now_time),'html', 'utf-8')
    msgroot.attach(message)

    # 邮箱的smtp服务器
    s = smtplib.SMTP_SSL(smtpserver, smtpport)
    s.connect(smtpserver)
    s.login(sender, password)

    # # 发送给多人、同时抄送给多人，发送人和抄送人放在同一个列表中
    s.sendmail(sender, receiver, msgroot.as_string())
    s.quit()