# 项目在https://github.com/inkcoo/birthdays_reminder开源免费
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import lunardate
import pytz  # 用于处理时区
import os  # 引入os模块来读取环境变量

# 读取生日文件
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

# 使用北京时间获取农历日期
def get_lunar_date_in_beijing():
    tz = pytz.timezone('Asia/Shanghai')  # 使用北京时间时区
    now = datetime.now(tz)  # 当前北京时间
    lunar_date = lunardate.LunarDate.fromSolarDate(now.year, now.month, now.day)
    return lunar_date

# 判断是否是今天生日
def is_birthday_today(date, calendar_type):
    tz = pytz.timezone('Asia/Shanghai')  # 使用北京时间
    today = datetime.now(tz)  # 获取当前的北京时间

    if calendar_type == 'a':  # 公历
        month, day = map(int, date.split('/'))
        return today.month == month and today.day == day
    elif calendar_type == 'b':  # 农历
        lunar_today = get_lunar_date_in_beijing()  # 基于北京时间的农历日期
        month, day = map(int, date.split('/'))
        return lunar_today.month == month and lunar_today.day == day
    return False

# 发送邮件
def send_email(subject, body, to_email):
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # SSL 端口
    smtp_user = os.getenv('SMTP_USER')  # 从环境变量读取账号
    smtp_password = os.getenv('SMTP_PASSWORD')  # 从环境变量读取密码

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    # 使用 SSL 发送邮件，适配 QQ 邮箱
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_email], msg.as_string())

# 主程序
def main():
    print("读取生日列表...")
    birthdays = read_birthdays('birthdays.txt')
    print("检查生日是否是今天...")

    # 添加管理员邮箱
    admin_email = os.getenv('ADMIN_EMAIL')  # 通过环境变量读取管理员邮箱

    # 存储当天生日成员的列表（包含名字和生日类型）
    today_birthdays = []

    for name, date, calendar_type in birthdays:
        if is_birthday_today(date, calendar_type):
            birthday_type = "(公历)" if calendar_type == 'a' else "(农历)"
            today_birthdays.append((name, birthday_type))
            print(f"今天是心助会- {name} {birthday_type} 的生日!")
        else:
            print(f"{name} 今天不是生日。")

    # 获取程序运行的本地时间并包含时区信息
    tz = pytz.timezone('Asia/Shanghai')  # 设置为中国时区
    now = datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")  # 包含时区名称
    print(f"程序运行时间: {formatted_time}\n项目在https://github.com/inkcoo/birthdays_reminder开源免费")

    # 如果有成员生日，发送邮件
    if today_birthdays:
        # 根据生日成员数量生成提醒内容
        if len(today_birthdays) == 1:
            # 只有一位成员生日
            name_with_type = f"{today_birthdays[0][0]} {today_birthdays[0][1]}"
            subject = f"生日提醒: 今天是心助会-{name_with_type} 的生日"
            body = f"今天是 {name_with_type} 的生日，请记得祝福 TA！\n\n邮件发送时间: {formatted_time}"
        else:
            # 多位成员生日
            names_with_types = "、".join([f"{name} {birthday_type}" for name, birthday_type in today_birthdays])
            subject = "生日提醒: 今天有多位成员的生日"
            body = f"今天是 {names_with_types} 的生日，请记得祝福他们！\n\n邮件发送时间: {formatted_time}"

        # 发送邮件给生日人
        send_email(subject, body, os.getenv('SMTP_USER'))
        print(f"生日提醒邮件已发送给成员，发送时间: {formatted_time}")

        # 发送邮件给管理员
        if admin_email:
            send_email(subject, body, admin_email)
            print(f"生日提醒邮件已发送给管理员 {admin_email}，发送时间: {formatted_time}")

if __name__ == "__main__":
    main()
