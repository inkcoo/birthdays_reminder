# 项目在https://github.com/inkcoo/birthdays_reminder开源免费
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import lunardate
import pytz
import os
import sys
import re

def read_birthdays(filename):
    """
    读取生日文件，并去除完全相同的重复行。
    支持两种格式：
    1. 姓名-年-月-日-类型 (e.g., 张三-2005-4-16-a)
    2. 姓名-月-日-类型 (e.g., 李四-1-9-b)
    """
    birthdays = []
    seen_lines = set()  # 用于跟踪已经出现的行内容以实现去重[1,9](@ref)
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            original_line = line.strip()
            if not original_line:
                continue
                
            # 去重：如果已经见过完全相同的行，则跳过[1,9](@ref)
            if original_line in seen_lines:
                print(f"发现重复行，已跳过: {original_line}")
                continue
            seen_lines.add(original_line)
            
            # 使用正则表达式匹配两种格式
            pattern_with_year = r'^(.+)-(\d{4})-(\d{1,2})-(\d{1,2})-(a|b)$'
            pattern_without_year = r'^(.+)-(\d{1,2})-(\d{1,2})-(a|b)$'
            
            match_with_year = re.match(pattern_with_year, original_line)
            match_without_year = re.match(pattern_without_year, original_line)
            
            if match_with_year:
                name, year, month, day, calendar_type = match_with_year.groups()
                birthdays.append({
                    'name': name,
                    'year': int(year),
                    'month': int(month),
                    'day': int(day),
                    'calendar_type': calendar_type,
                    'has_year': True
                })
            elif match_without_year:
                name, month, day, calendar_type = match_without_year.groups()
                birthdays.append({
                    'name': name,
                    'year': None,
                    'month': int(month),
                    'day': int(day),
                    'calendar_type': calendar_type,
                    'has_year': False
                })
            else:
                print(f"跳过格式不正确的行: {original_line}")
    return birthdays

def get_lunar_date_in_beijing():
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    lunar_date = lunardate.LunarDate.fromSolarDate(now.year, now.month, now.day)
    return lunar_date

def calculate_age(birthday_info):
    """计算年龄（仅适用于有年份的情况）"""
    if not birthday_info['has_year']:
        return None
        
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)
    calendar_type = birthday_info['calendar_type']
    birth_year = birthday_info['year']
    birth_month = birthday_info['month']
    birth_day = birthday_info['day']
    
    if calendar_type == 'a':  # 公历
        age = today.year - birth_year
        # 检查今年生日是否已过
        if (today.month, today.day) < (birth_month, birth_day):
            age -= 1
        return age
    elif calendar_type == 'b':  # 农历
        try:
            # 将农历生日转换为公历日期来计算年龄
            solar_date = lunardate.LunarDate(birth_year, birth_month, birth_day).toSolar()
            age = today.year - solar_date.year
            # 检查今年生日是否已过
            if (today.month, today.day) < (solar_date.month, solar_date.day):
                age -= 1
            return age
        except Exception as e:
            print(f"农历年龄计算错误: {e}")
            return None
    return None

def is_birthday_today(birthday_info):
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)
    calendar_type = birthday_info['calendar_type']

    if calendar_type == 'a':  # 公历
        return today.month == birthday_info['month'] and today.day == birthday_info['day']
    elif calendar_type == 'b':  # 农历
        lunar_today = get_lunar_date_in_beijing()
        return lunar_today.month == birthday_info['month'] and lunar_today.day == birthday_info['day']
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
        print(f"邮件发送成功但遇到连接关闭异常(可忽略): {e}")
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

    for birthday_info in birthdays:
        if is_birthday_today(birthday_info):
            # 计算年龄（如果有年份信息）
            age_info = ""
            if birthday_info['has_year']:
                age = calculate_age(birthday_info)
                if age is not None:
                    age_info = f"，{age}岁"
            
            birthday_type = "(公历)" if birthday_info['calendar_type'] == 'a' else "(农历)"
            today_birthdays.append({
                'name': birthday_info['name'],
                'type': birthday_type,
                'age_info': age_info
            })
            print(f"今天是心助会- {birthday_info['name']} {birthday_type}{age_info} 的生日!")
        else:
            print(f"{birthday_info['name']} 今天不是生日。")

    print(f"程序运行时间: {formatted_time}\n项目在https://github.com/inkcoo/birthdays_reminder开源免费")

    exit_code = 0  # 默认成功状态码
    
    if today_birthdays:
        if len(today_birthdays) == 1:
            birthday = today_birthdays[0]
            name_with_type = f"{birthday['name']} {birthday['type']}"
            subject = f"生日提醒: 今天是心助会-{name_with_type}的生日"
            body = f"今天是 {name_with_type}{birthday['age_info']} 的生日，请记得祝福 TA！\n\n邮件发送时间: {formatted_time}\n\n来自github自动任务"
        else:
            names_with_types = "、".join([f"{b['name']} {b['type']}{b['age_info']}" for b in today_birthdays])
            subject = "生日提醒: 今天有多位成员的生日"
            body = f"今天是 {names_with_types} 的生日，请记得祝福他们！\n\n邮件发送时间: {formatted_time}\n\n来自github自动任务"

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
