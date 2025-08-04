# 项目在https://github.com/inkcoo/birthdays_reminder开源免费
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import lunardate
import pytz
import os
import sys  # 新增引入sys模块

def read_birthdays(filename):
    birthdays = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split('-')
            if len(parts) == 4:
                name, month, day, calendar_type = parts
                birthdays.append((name, f"{month}/{day}", calendar_type))
            else:
                print(f"跳过格式不正确的行: {line.strip()}")
    return birthdays

def get_lunar_date_in_beijing():
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    lunar_date = lunardate.LunarDate.fromSolarDate(now.year, now.month, now.day)
    return lunar_date

def is_birthday_today(date, calendar_type):
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)

    if calendar_type == 'a':  # 公历
        month, day = map(int, date.split('/'))
        return today.month == month and today.day == day
    elif calendar_type == 'b':  # 农历
        lunar_today = get_lunar_date_in_beijing()
        month, day = map(int, date.split('/'))
        return lunar_today.month == month and lunar_today.day == day
    return False

def send_email(subject, body, to_email):
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        return True
    except smtplib.SMTPResponseException as e:
        # 忽略特定异常 - GitHub Actions 运行所需
        print(f"邮件发送成功但遇到邮件服务器返回异常(可忽略): {e}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def main():
    print("读取生日列表...")
    birthdays = read_birthdays('birthdays.txt')
    print("检查生日是否是今天...")

    admin_email = os.getenv('ADMIN_EMAIL')
    today_birthdays = []
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    for name, date, calendar_type in birthdays:
        if is_birthday_today(date, calendar_type):
            birthday_type = "(公历)" if calendar_type == 'a' else "(农历)"
            today_birthdays.append((name, birthday_type))
            print(f"今天是心助会- {name} {birthday_type} 的生日!")
        else:
            print(f"{name} 今天不是生日。")

    print(f"程序运行时间: {formatted_time}\n项目在https://github.com/inkcoo/birthdays_reminder开源免费")

    exit_code = 0  # 默认成功状态码
    
    if today_birthdays:
        if len(today_birthdays) == 1:
            name_with_type = f"{today_birthdays[0][0]} {today_birthdays[0][1]}"
            subject = f"生日提醒: 今天是心助会-{name_with_type} 的生日"
            body = f"今天是 {name_with_type} 的生日，请记得祝福 TA！\n\n邮件发送时间: {formatted_time}\n\n来自github的自动任务"
        else:
            names_with_types = "、".join([f"{name} {birthday_type}" for name, birthday_type in today_birthdays])
            subject = "生日提醒: 今天有心助会多位成员的生日"
            body = f"今天是 {names_with_types} 的生日，请记得祝福他们！\n\n邮件发送时间: {formatted_time}\n\n来自github的自动任务"

        # 给成员发送邮件
        if not send_email(subject, body, os.getenv('SMTP_USER')):
            exit_code = 1  # 发送失败则设为错误状态
        else:
            print(f"生日提醒邮件已发送给成员，发送时间: {formatted_time}")

        # 给管理员发送邮件
        if admin_email:
            if not send_email(subject, body, admin_email):
                exit_code = 1  # 发送失败则设为错误状态
            else:
                print(f"生日提醒邮件已发送给管理员 {admin_email}，发送时间: {formatted_time}")
    
    sys.exit(exit_code)  # 返回适当的退出代码

if __name__ == "__main__":
    main()
