# 生日提醒系统 - 本地部署版本
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import lunardate
import pytz
import os
import sys
import re
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('email.env')

def read_birthdays(filename):
    """读取生日列表文件"""
    birthdays = []
    if not os.path.exists(filename):
        print(f"错误：找不到文件 {filename}")
        return birthdays
        
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            # 匹配四种格式
            patterns = [
                r'^(.+)-(\d{4})-(\d{1,2})-(\d{1,2})-(a|b)-(.+)$',  # 姓名-年-月-日-类型-部门
                r'^(.+)-(\d{1,2})-(\d{1,2})-(a|b)-(.+)$',          # 姓名-月-日-类型-部门
                r'^(.+)-(\d{4})-(\d{1,2})-(\d{1,2})-(a|b)$',      # 姓名-年-月-日-类型
                r'^(.+)-(\d{1,2})-(\d{1,2})-(a|b)$'               # 姓名-月-日-类型
            ]
            
            for i, pattern in enumerate(patterns):
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    if i in [0, 1]:  # 带部门
                        if i == 0:  # 带年份带部门
                            name, year, month, day, calendar_type, department = groups
                            year = int(year)
                        else:  # 不带年份带部门
                            name, month, day, calendar_type, department = groups
                            year = None
                    else:  # 不带部门
                        if i == 2:  # 带年份不带部门
                            name, year, month, day, calendar_type = groups
                            year = int(year)
                        else:  # 不带年份不带部门
                            name, month, day, calendar_type = groups
                            year = None
                        department = None
                    
                    birthdays.append({
                        'name': name,
                        'year': year,
                        'month': int(month),
                        'day': int(day),
                        'calendar_type': calendar_type,
                        'department': department,
                        'has_year': year is not None,
                        'has_department': department is not None
                    })
                    break
            else:
                print(f"跳过格式错误的行: {line}")
    
    return birthdays

def calculate_age(birthday_info):
    """计算年龄"""
    if not birthday_info['has_year']:
        return None
    
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)
    
    if birthday_info['calendar_type'] == 'a':  # 公历
        age = today.year - birthday_info['year']
        if (today.month, today.day) < (birthday_info['month'], birthday_info['day']):
            age -= 1
        return age
    else:  # 农历
        try:
            solar_date = lunardate.LunarDate(birthday_info['year'], birthday_info['month'], birthday_info['day']).toSolarDate()
            age = today.year - solar_date.year
            if (today.month, today.day) < (solar_date.month, solar_date.day):
                age -= 1
            return age
        except Exception as e:
            print(f"农历年龄计算错误: {e}")
            return None

def is_birthday_today(birthday_info):
    """检查是否是今天生日"""
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)
    
    if birthday_info['calendar_type'] == 'a':  # 公历
        return today.month == birthday_info['month'] and today.day == birthday_info['day']
    else:  # 农历
        lunar_today = lunardate.LunarDate.fromSolarDate(today.year, today.month, today.day)
        return lunar_today.month == birthday_info['month'] and lunar_today.day == birthday_info['day']

def format_display(birthday_info):
    """格式化显示信息"""
    name = birthday_info['name']
    department = birthday_info.get('department')
    calendar_type = "(公历)" if birthday_info['calendar_type'] == 'a' else "(农历)"
    
    age_info = ""
    if birthday_info['has_year']:
        age = calculate_age(birthday_info)
        if age is not None:
            age_info = f"，{age}岁"
    
    if department:
        return f"({department}) {name} {calendar_type}{age_info}"
    else:
        return f"{name} {calendar_type}{age_info}"

def send_email(subject, body, to_email):
    """发送邮件"""
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not all([smtp_user, smtp_password]):
        print("错误：邮件配置不完整，请检查 email.env 文件")
        return False
    
    # 创建邮件内容对象，支持HTML格式
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def main():
    print("=== 生日提醒系统启动 ===")
    
    # 检查必要文件
    if not os.path.exists('email.env'):
        print("错误：找不到 email.env 文件，请创建邮箱配置文件")
        return
    
    if not os.path.exists('birthdays.txt'):
        print("错误：找不到 birthdays.txt 文件，请创建生日列表文件")
        return
    
    # 读取生日列表
    birthdays = read_birthdays('birthdays.txt')
    if not birthdays:
        print("警告：没有找到有效的生日记录")
        return
    
    print(f"成功加载 {len(birthdays)} 条生日记录")
    
    # 检查今日生日
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S UTC+8")
    
    today_birthdays = []
    for birthday_info in birthdays:
        if is_birthday_today(birthday_info):
            today_birthdays.append(birthday_info)
    
    # 显示结果
    print(f"\n运行时间: {formatted_time}")
    print("="*50)
    
    if today_birthdays:
        print(f"今日生日总结 ({len(today_birthdays)}人):")
        for i, birthday in enumerate(today_birthdays, 1):
            display_name = format_display(birthday)
            print(f"{i}. 心助会- {display_name}")
        
        # 发送邮件
        admin_email = os.getenv('ADMIN_EMAIL')
        if admin_email:
            if len(today_birthdays) == 1:
                birthday = today_birthdays[0]
                display_name = format_display(birthday)
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
                            <p>发送时间: {formatted_time}<br>
                            来自本地自动任务</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            else:
                subject = "生日提醒: 今天有多位成员的生日"
                # 构建HTML格式的生日列表
                birthday_list_html = ""
                for i, birthday in enumerate(today_birthdays, 1):
                    display_name = format_display(birthday)
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
                            <p>发送时间: {formatted_time}<br>
                            来自本地自动任务</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            if send_email(subject, body, admin_email):
                print(f"✓ 邮件已发送至管理员: {admin_email}")
            else:
                print("✗ 邮件发送失败")
        else:
            print("警告：未配置 ADMIN_EMAIL，跳过邮件发送")
    else:
        print("今日生日总结: 今天没有人过生日。")
    
    print("="*50)
    print("=== 程序运行完成 ===")

if __name__ == "__main__":
    main()
