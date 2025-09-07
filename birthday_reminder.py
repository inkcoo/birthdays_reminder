# 项目在https://github.com/inkcoo/birthdays_reminder开源免费
import smtplib  # 用于发送邮件
from email.mime.text import MIMEText  # 用于构建邮件内容
from datetime import datetime  # 用于处理日期和时间
import lunardate  # 用于农历日期转换
import pytz  # 用于时区处理
import os  # 用于访问环境变量和系统操作
import sys  # 用于系统相关操作
import re  # 用于正则表达式匹配


def read_birthdays(filename):
    """
    从文件中读取生日信息
    
    参数:
        filename: 包含生日数据的文件名
        
    返回:
        包含所有生日信息的字典列表
        支持四种格式:
        1. 姓名-年-月-日-类型 (带年份不带部门)
        2. 姓名-月-日-类型 (不带年份不带部门)
        3. 姓名-月-日-类型-部门 (不带年份带部门)
        4. 姓名-年-月-日-类型-部门 (带年份带部门)
        
    类型说明:
        a: 公历生日
        b: 农历生日
    """
    birthdays = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # 去除首尾空白字符
            if not line:  # 跳过空行
                continue
            
            # 定义四种正则表达式模式匹配不同的生日格式
            pattern1 = r'^(.+)-(\d{4})-(\d{1,2})-(\d{1,2})-(a|b)$'  # 格式1: 姓名-年-月-日-类型
            pattern2 = r'^(.+)-(\d{1,2})-(\d{1,2})-(a|b)$'  # 格式2: 姓名-月-日-类型
            pattern3 = r'^(.+)-(\d{1,2})-(\d{1,2})-(a|b)-(.+)$'  # 格式3: 姓名-月-日-类型-部门
            pattern4 = r'^(.+)-(\d{4})-(\d{1,2})-(\d{1,2})-(a|b)-(.+)$'  # 格式4: 姓名-年-月-日-类型-部门
            
            # 按优先级尝试匹配四种格式
            match4 = re.match(pattern4, line)
            match3 = re.match(pattern3, line)
            match1 = re.match(pattern1, line)
            match2 = re.match(pattern2, line)
            
            if match4:  # 格式4: 带年份带部门
                name, year, month, day, calendar_type, department = match4.groups()
                birthdays.append({
                    'name': name,
                    'year': int(year),
                    'month': int(month),
                    'day': int(day),
                    'calendar_type': calendar_type,  # a=公历, b=农历
                    'department': department,
                    'has_year': True,
                    'has_department': True
                })
            elif match3:  # 格式3: 不带年份带部门
                name, month, day, calendar_type, department = match3.groups()
                birthdays.append({
                    'name': name,
                    'year': None,
                    'month': int(month),
                    'day': int(day),
                    'calendar_type': calendar_type,
                    'department': department,
                    'has_year': False,
                    'has_department': True
                })
            elif match1:  # 格式1: 带年份不带部门
                name, year, month, day, calendar_type = match1.groups()
                birthdays.append({
                    'name': name,
                    'year': int(year),
                    'month': int(month),
                    'day': int(day),
                    'calendar_type': calendar_type,
                    'department': None,
                    'has_year': True,
                    'has_department': False
                })
            elif match2:  # 格式2: 不带年份不带部门
                name, month, day, calendar_type = match2.groups()
                birthdays.append({
                    'name': name,
                    'year': None,
                    'month': int(month),
                    'day': int(day),
                    'calendar_type': calendar_type,
                    'department': None,
                    'has_year': False,
                    'has_department': False
                })
            else:
                print(f"跳过格式不正确的行: {line}")
    return birthdays


def get_lunar_date_in_beijing():
    """
    获取北京时间的当前农历日期
    
    返回:
        LunarDate对象，包含当前农历年月日信息
    """
    tz = pytz.timezone('Asia/Shanghai')  # 设置时区为北京时间
    now = datetime.now(tz)  # 获取当前时间
    lunar_date = lunardate.LunarDate.fromSolarDate(now.year, now.month, now.day)  # 将公历转换为农历
    return lunar_date


def calculate_age(birthday_info):
    """
    计算年龄（仅适用于有年份的情况）
    
    参数:
        birthday_info: 包含生日信息的字典
        
    返回:
        年龄数值（整数）或None（无年份信息时）
    """
    if not birthday_info['has_year']:  # 检查是否有年份信息
        return None
        
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)  # 获取当前日期
    calendar_type = birthday_info['calendar_type']
    birth_year = birthday_info['year']
    birth_month = birthday_info['month']
    birth_day = birthday_info['day']
    
    if calendar_type == 'a':  # 公历生日
        age = today.year - birth_year  # 计算年份差
        # 如果今年生日还没过，年龄减1
        if (today.month, today.day) < (birth_month, birth_day):
            age -= 1
        return age
    elif calendar_type == 'b':  # 农历生日
        try:
            # 将农历生日转换为公历日期
            solar_date = lunardate.LunarDate(birth_year, birth_month, birth_day).toSolarDate()
            age = today.year - solar_date.year
            # 如果今年生日还没过，年龄减1
            if (today.month, today.day) < (solar_date.month, solar_date.day):
                age -= 1
            return age
        except Exception as e:
            print(f"农历年龄计算错误: {e}")
            return None
    return None


def is_birthday_today(birthday_info):
    """
    检查今天是否是某人的生日
    
    参数:
        birthday_info: 包含生日信息的字典
        
    返回:
        True表示今天是生日，False表示不是
    """
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)  # 获取当前日期
    calendar_type = birthday_info['calendar_type']

    if calendar_type == 'a':  # 公历生日
        # 比较月份和日期是否匹配
        return today.month == birthday_info['month'] and today.day == birthday_info['day']
    elif calendar_type == 'b':  # 农历生日
        lunar_today = get_lunar_date_in_beijing()  # 获取当前农历日期
        # 比较农历月份和日期是否匹配
        return lunar_today.month == birthday_info['month'] and lunar_today.day == birthday_info['day']
    return False


def format_birthday_display(birthday_info):
    """
    格式化生日显示信息
    
    参数:
        birthday_info: 包含生日信息的字典
        
    返回:
        格式化后的生日显示字符串
    """
    name = birthday_info['name']
    department = birthday_info.get('department')  # 获取部门信息（可能为None）
    calendar_type = "(公历)" if birthday_info['calendar_type'] == 'a' else "(农历)"  # 日历类型显示
    
    # 计算年龄（如果有年份信息）
    age_info = ""
    if birthday_info['has_year']:
        age = calculate_age(birthday_info)
        if age is not None:
            age_info = f"，{age}岁"
    
    # 根据是否有部门信息构建不同的显示格式
    if department:
        display_name = f"({department}) {name} {calendar_type}{age_info}"
    else:
        display_name = f"{name} {calendar_type}{age_info}"
    
    return display_name


def send_email(subject, body, to_email):
    """
    发送电子邮件
    
    参数:
        subject: 邮件主题
        body: 邮件正文内容
        to_email: 收件人邮箱地址
        
    返回:
        True表示发送成功，False表示发送失败
        
    注意:
        需要使用环境变量设置SMTP_USER和SMTP_PASSWORD
        默认使用QQ邮箱SMTP服务器，可根据需要修改
    """
    smtp_server = "smtp.qq.com"  # QQ邮箱SMTP服务器
    smtp_port = 465  # SSL端口
    smtp_user = os.getenv('SMTP_USER')  # 从环境变量获取发件人邮箱
    smtp_password = os.getenv('SMTP_PASSWORD')  # 从环境变量获取邮箱授权码

    # 创建邮件内容对象，支持HTML格式
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = subject  # 设置邮件主题
    msg['From'] = smtp_user  # 设置发件人
    msg['To'] = to_email  # 设置收件人

    try:
        # 使用SSL连接SMTP服务器并发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)  # 登录邮箱
            server.sendmail(smtp_user, [to_email], msg.as_string())  # 发送邮件
        return True
    except smtplib.SMTPResponseException as e:
        # 处理可能的SMTP响应异常（有时发送成功但仍会抛出异常）
        print(f"邮件发送成功但遇到连接关闭异常(可忽略): {e}")
        return True
    except Exception as e:
        # 处理其他发送异常
        print(f"邮件发送失败: {e}")
        return False


def main():
    """
    主函数：协调整个生日提醒流程
    """
    print("读取生日列表...")
    birthdays = read_birthdays('birthdays.txt')  # 从文件读取生日数据
    print("检查生日是否是今天...")

    admin_email = os.getenv('ADMIN_EMAIL')  # 从环境变量获取管理员邮箱
    today_birthdays = []  # 存储今天过生日的所有人
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)  # 获取当前时间
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S UTC+8")  # 格式化时间显示

    # 遍历所有生日记录，检查是否是今天生日
    for birthday_info in birthdays:
        if is_birthday_today(birthday_info):
            today_birthdays.append(birthday_info)  # 添加到今天生日列表
            display_name = format_birthday_display(birthday_info)
            print(f"今天是心助会- {display_name} 的生日!")
        else:
            display_name = format_birthday_display(birthday_info)
            print(f"{display_name} 今天不是生日。")

    # 显示程序运行时间和项目信息
    print(f"程序运行时间: {formatted_time}\n项目在https://github.com/inkcoo/birthdays_reminder  开源免费")

    # 在控制台总结输出当天生日人员
    print("\n" + "="*50)
    if today_birthdays:
        print(f"今日生日总结 ({len(today_birthdays)}人):")
        for i, birthday in enumerate(today_birthdays, 1):
            display_name = format_birthday_display(birthday)
            print(f"{i}. 心助会- {display_name}")
    else:
        print("今日生日总结: 今天没有人过生日。")
    print("="*50)

    exit_code = 0  # 退出代码，0表示成功，1表示有错误
    
    # 处理今天有生日的情况
    if today_birthdays:
        if len(today_birthdays) == 1:
            # 单人生日邮件内容
            birthday = today_birthdays[0]
            display_name = format_birthday_display(birthday)
            subject = f"生日提醒: 今天是心助会-{display_name}的生日"
            # 使用HTML格式的邮件内容
            body = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 5px; }}
                    .content {{ padding: 20px; }}
                    .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
                    .highlight {{ color: #007bff; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🎂 生日提醒</h2>
                    </div>
                    <div class="content">
                        <p>今天是心助会- <span class="highlight">{display_name}</span> 的生日，请记得祝福 TA！</p>
                    </div>
                    <div class="footer">
                        <p>邮件发送时间: {formatted_time}<br>
                        来自 GitHub 自动任务</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            # 多人生日邮件内容
            subject = "生日提醒: 今天有多位成员的生日"
            # 构建HTML格式的生日列表
            birthday_list_html = ""
            for i, birthday in enumerate(today_birthdays, 1):
                display_name = format_birthday_display(birthday)
                birthday_list_html += f"<li>心助会- {display_name}</li>"
            
            # 使用HTML格式的邮件内容
            body = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 5px; }}
                    .content {{ padding: 20px; }}
                    .birthday-list {{ padding-left: 20px; }}
                    .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
                    .highlight {{ color: #007bff; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🎂 生日提醒</h2>
                    </div>
                    <div class="content">
                        <p>今天有多名成员的生日：</p>
                        <ol class="birthday-list">
                            {birthday_list_html}
                        </ol>
                        <p class="highlight">请记得送上祝福哦 🎉</p>
                    </div>
                    <div class="footer">
                        <p>邮件发送时间: {formatted_time}<br>
                        来自 GitHub 自动任务</p>
                    </div>
                </div>
            </body>
            </html>
            """

        # 发送邮件给成员（使用SMTP_USER环境变量）
        if not send_email(subject, body, os.getenv('SMTP_USER')):
            exit_code = 1  # 发送失败时设置错误代码
        else:
            print(f"生日提醒邮件已发送给成员，发送时间: {formatted_time}")

        # 发送邮件给管理员（如果设置了ADMIN_EMAIL环境变量）
        if admin_email:
            if not send_email(subject, body, admin_email):
                exit_code = 1  # 发送失败时设置错误代码
            else:
                print(f"生日提醒邮件已发送给管理员 {admin_email}，发送时间: {formatted_time}")
    
    sys.exit(exit_code)  # 退出程序并返回退出代码


if __name__ == "__main__":
    main()  # 程序入口点
