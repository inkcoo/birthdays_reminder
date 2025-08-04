
# birthdays_reminder 🎂

> 一个免费的成员生日邮件提醒工具，适用于行政部门、社团和好友群体。它能够读取生日列表（支持公历和农历），在生日当天自动发送邮件提醒，方便我们为成员送上生日祝福。作者：INKCOO(ixiaocang/Hitori/小东/修兮求索/radish)

## 目录 📚

- [项目简介](#项目简介-ℹ️)
- [功能特点](#功能特点-✨)
- [使用方法](#使用方法)
- [许可证](#许可证-📄)
- [更新日志](#更新日志-📅)2025.8.4/最新

## 项目简介 ℹ️

这是一个用于生日提醒的 Python 程序，它可以通过读取生日列表，在生日当天自动发送邮件给自己，方便我们给成员的生日祝福。支持公历(阳历)和农历(阴历)生日提醒，适用于使用 QQ 邮箱发送邮件。生日提醒邮件不仅会发送给自己，还会发送一份提醒邮件给负责管理员。项目为我想记得给校心助会成员生日祝福初衷设计。

作者 INKCOO (ixiaocang/Hitori/小东/修兮求索/radish) 目前是一名日语专业的本科生，在计算机领域还在学习中，计算机超级菜鸟一个。这个程序是在 2024 年 10 月 12 日利用 AI 辅助创建的。如果您有任何问题或建议，请发送邮件至 ixiaocang@foxmail.com，欢迎提出宝贵意见。

## 功能特点 ✨

- **生日提醒**：支持公历(阳历)和农历(阴历)（含闰月）生日提醒，自动判断当天生日。
- **邮件发送**：在生日当天自动发送提醒邮件给自己和管理员。
- **日志记录**：记录程序启动、结束时间及运行时长。
- **可配置性**：通过环境变量配置邮箱账号、密码和管理员邮箱，确保信息安全。

## 使用方法 🛠️

### [一、GitHub免费Fork使用](#1-克隆到自己的仓库-📦)
### [二、服务器部署](#61-部署到本地服务器-🖥️)

### 一、GitHub免费Fork使用
 #1. 克隆到自己的仓库 📦

在 GitHub 上fork项目，完成初始设置。可设置为隐私仓库，避免被人查看你的生日列表。

### 2. 配置生日列表 📝

在项目根目录的 `birthdays.txt` 文件中，按照如下格式一行一个添加成员的生日信息：

```txt
姓名-月-日-公历或农历类型
张三-10-12-a
李四-08-15-b
```

- **a** 代表公历
- **b** 代表农历

### 3. 配置邮件客户端 📧

1. 登录你的 QQ 邮箱。
2. 点击右上角的 “设置” 图标，选择 “账户” 选项。
3. 找到 **SMTP 服务** 部分，点击开启，并生成授权码。这段授权码将作为 **SMTP_PASSWORD** 用于程序中。

### 4. 设置 GitHub 仓库 Secrets 🔐

1. 打开项目仓库的 **Settings** 页面。
2. 进入 **Secrets and variables > Actions** 部分，点击 **New repository secret**。
3. 添加以下三个 Secret：
   - **SMTP_USER**：你的 QQ 邮箱。
   - **SMTP_PASSWORD**：生成的授权码。
   - **ADMIN_EMAIL**：管理员邮箱，抄送生日提醒给管理员。

### 5. 修改 GitHub Actions 工作流运行时间 ⏱️

项目默认会每天北京时间上午 6:05 运行且不受时区影响，如需修改，打开 `.github/workflows/birthday_reminder.yml` 文件，调整 `cron` 配置即可：

```yaml
- cron: '15 22 * * *'  # 北京时间早上6点15（22+8为次日六点）
- cron: '0 22 * * *'   # 北京时间早上6点
```
### 到此你的项目就差不多配置好了，最后需要在仓库Action 的Birthday Reminder工作流中启用工作流，手动运行测试一下，之后便可自动运行

### 5.1 工作流保活：避免60天仓库无提交导致工作流禁用 💪
配置文件`birthdays_reminder\.github\workflows\keep_active.yml`

1. 在仓库 `Settings > Actions > General` 页面
2. 找到 "Workflow permissions" 部分
3. 勾选 "Read and write permissions"
4. 点击 Save 按钮
5. 接着启用工作流
6. 提交文件后，转到仓库的 "Actions" 标签页
7. 找到 "Keep Repository Active" 工作流
8. 点击 "Enable workflow"

---
***

### 6.1 部署到本地服务器 🖥️

如需部署到本地服务器，只需复制以下 Python 代码并保存为 `birthdays_reminder.py`，并安装依赖。

```python
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import lunardate
import pytz
from dotenv import load_dotenv
import os

load_dotenv('email.env')

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

    if calendar_type == 'a':
        month, day = map(int, date.split('/'))
        return today.month == month and today.day == day
    elif calendar_type == 'b':
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

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_email], msg.as_string())

def main():
    print("读取生日列表...")
    birthdays = read_birthdays('birthdays.txt')
    print("检查生日是否是今天...")

    admin_email = os.getenv('ADMIN_EMAIL')

    today_birthdays = []

    for name, date, calendar_type in birthdays:
        if is_birthday_today(date, calendar_type):
            birthday_type = "(公历)" if calendar_type == 'a' else "(农历)"
            today_birthdays.append((name, birthday_type))
            print(f"今天是 {name} 的生日 {birthday_type}!")
        else:
            print(f"{name} 今天不是生日。")

    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    if today_birthdays:
        if len(today_birthdays) == 1:
            name_with_type = f"{today_birthdays[0][0]} {today_birthdays[0][1]}"
            subject = f"生日提醒: 今天是 {name_with_type} 的生日"
            body = f"今天是 {name_with_type} 的生日，请记得祝福 TA！\n\n邮件发送时间: {formatted_time}"
        else:
            names_with_types = "、".join([f"{name} {birthday_type}" for name, birthday_type in today_birthdays])
            subject = "生日提醒: 今天有多位成员的生日"
            body = f"今天是 {names_with_types} 的生日，请记得祝福他们！\n\n邮件发送时间: {formatted_time}"

        send_email(subject, body, os.getenv('SMTP_USER'))
        print(f"生日提醒邮件已发送给成员，发送时间: {formatted_time}")

        if admin_email:
            send_email(subject, body, admin_email)
            print(f"生日提醒邮件已发送给管理员 {admin_email}，发送时间: {formatted_time}")

if __name__ == "__main__":
    main()
```

### 6.2 配置环境变量 ⚙️

在同目录创建 `email.env` 文件，存储邮箱信息：

```txt
SMTP_USER=your_smtp_user@example.com
SMTP_PASSWORD=your_smtp_password
ADMIN_EMAIL=your_admin_email@example.com
```
以及创建`birthdays.txt`生日列表文件
### 6.3 安装依赖（python3）📦

```bash
pip3 install python-dotenv smtplib pytz lunardate
```
### 6.4 自动运行 ⏰
配置好后通过计划任务`python3 birthdays_reminder.py`运行就好了

## 许可证 📄

本项目采用 **[GPL3.0](https://www.gnu.org/licenses/gpl-3.0.en.html#license-text)** 进行许可。你可以免费使用、修改和分发本项目的代码，但必须遵守GPL3.0的许可证条款。如需商业许可，请联系作者ixiaocang@fomail.com。


## 更新日志 📅

**2025.8.4更新，新增了工作流保活的配置文件，避免60天仓库无提交导致工作流禁用，修复了github actions 控制台返回报错问题
,修改介绍文档，修改许可证为GPL3.0**

**2024.10.15晚更新，在邮件和后台窗口日志中添加成员生日是属于农历还是公历**

**2024.10.16早更新，修改的生日判断改为用北京时间判断，避免github运行的时区影响**

**2024.10.17早更新，修改的农历时间及生日判断改为用北京时间判断，避免github运行的时区影响**
