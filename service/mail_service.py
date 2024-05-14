import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_code(email):
    # 生成6位随机验证码
    verification_code = ''.join(random.choices('0123456789', k=6))

    # 设置发件人和收件人邮箱地址
    sender_email = "496812133@qq.com"
    receiver_email = email

    # 创建邮件内容
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "验证码"

    body = f"您的验证码是：{verification_code}"
    msg.attach(MIMEText(body, 'plain'))

    # 发送邮件
    with smtplib.SMTP('smtp.example.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, "your_password")
        smtp.send_message(msg)

    print("验证码已发送至您的邮箱，请查收。")

# 在此处调用函数，并传入接收验证码的邮箱地址

send_verification_code("recipient_email@example.com")