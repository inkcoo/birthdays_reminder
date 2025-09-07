
# birthdays_reminder 🎂

> 这是一个基于Python开发的自动化生日提醒系统，专为记住重要日子而设计。系统通过读取生日列表文件，在对应的生日当天自动给你和负责管理员发送邮件提醒，确保你永远不会错过给亲朋好友、同事或团队成员送上生日祝福的机会。
作者：INKCOO(ixiaocang/Hitori/小东/修兮求索/radish)

## 目录 📚

- [ℹ️项目简介](#项目简介-ℹ️)
- [✨功能特点](#功能特点-✨)
- [🛠️使用方法](#使用方法-🛠️)
- [📄许可证](#许可证-📄)
- [📅更新日志](#更新日志-📅) - 最新更新于 2025.9.7（⭐请确保 fork 了最新仓库）


## 项目简介 ℹ️

这是一个用于生日提醒的 Python 程序，它可以通过读取生日列表，在生日当天自动发送邮件给自己，方便我们给成员的生日祝福。支持公历(阳历)和农历(阴历)生日提醒，适用于使用 QQ 邮箱发送邮件。生日提醒邮件不仅会发送给自己，还会发送一份提醒邮件给负责管理员。项目初衷为我想提醒自己给校心助会成员送生日祝福而设计。

作者 INKCOO (ixiaocang/Hitori/小东/修兮求索/radish) 目前是一名日语专业的本科生，在计算机领域还在学习中，计算机超级菜鸟一个。这个程序是在 2024 年 10 月 12 日利用 AI 辅助创建的。如果您有任何问题或建议，请发送邮件至 ixiaocang@foxmail.com，欢迎提出宝贵意见。
**适用场景：**
- 🏢 企业行政部门管理员工生日
- 🎓 学校社团管理成员生日
- 👥 朋友圈生日提醒
- 💼 团队管理者关怀成员

## 功能特点 ✨

- **生日提醒**：支持公历(阳历)和农历(阴历)（含闰月）生日提醒，自动判断当天生日。
- **邮件发送**：在生日当天自动发送提醒邮件给自己和管理员。
- **日志记录**：记录程序启动、结束时间及运行时长。
- **可配置性**：通过环境变量配置邮箱账号、密码和管理员邮箱，确保信息安全。
- **年龄显示**：支持显示成员年龄（可选，需要在生日列表中包含年份）。
- **部门显示**：支持显示成员所属部门（可选，需要在生日列表中包含部门信息）。

## 使用方法 🛠️

### [一、GitHub免费Fork使用](#一github免费fork使用-)
### [二、服务器部署](#61-本地-服务器快速部署-)

### 一、GitHub免费Fork使用
 #1. 克隆到自己的仓库 📦

在 GitHub 上fork项目，完成初始设置。可设置为隐私仓库，避免被人查看你的生日列表。

### 2. 配置生日列表 📝

在项目根目录的 `birthdays.txt` 文件中，按照如下格式一行一个添加成员的生日信息：

```txt
# 支持四种格式:
# 1. 姓名-年-月-日-类型 (带年份不带部门)
# 2. 姓名-月-日-类型 (不带年份不带部门)
# 3. 姓名-月-日-类型-部门 (不带年份带部门)
# 4. 姓名-年-月-日-类型-部门 (带年份带部门)

# 示例：
张三-1990-10-12-a
李四-08-15-b
王五-1985-05-20-a-技术部
赵六-12-25-b-市场部
```

- **a** 代表公历
- **b** 代表农历
- 如果包含年份，将显示年龄
- 如果包含部门，将显示部门信息

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
   - **ADMIN_EMAIL**：管理员邮箱（可选），抄送生日提醒给管理员。

### 5. 修改 GitHub Actions 工作流运行时间 ⏱️

项目默认会每天北京时间上午 6:05 运行且不受时区影响(但会受到github计划任务系统延迟，运行推迟约半个小时)，如需修改，打开 `.github/workflows/birthday_reminder.yml` 文件，调整 `cron` 配置即可：

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

### 6.1 本地 服务器快速部署 🚀
如遇到问题，请先浏览[一、GitHub免费Fork使用](#一github免费fork使用)了解项目基本使用方法，或咨询AI助手。

1. 下载文件 [birthday_reminder-local.py](https://raw.githubusercontent.com/inkcoo/birthdays_reminder/main/birthday_reminder-local.py) ：
```bash
# 创建项目目录
mkdir birthday_reminder && cd birthday_reminder

# 下载主程序（保存为 birthday_reminder.py）
curl -o birthday_reminder.py https://raw.githubusercontent.com/inkcoo/birthdays_reminder/main/birthday_reminder-local.py
```

2. 配置环境变量 ⚙️

同目录创建 `email.env` 文件：

```txt
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_qq_auth_code
ADMIN_EMAIL=admin@example.com
```

3. 创建生日列表 📋

同目录创建 `birthdays.txt` 文件：

```txt
张三-2000-01-15-a-技术部
李四-1995-03-22-b-市场部
王五-08-30-a-人事部
赵六-12-05-b
```

4. 安装依赖 📦

```bash
# 安装所需库
pip3 install python-dotenv pytz lunardate

# 验证安装
python3 -c "import dotenv, pytz, lunardate; print('依赖安装成功')"
```

5. 测试运行 🧪

```bash
# 手动测试
python3 birthday_reminder.py

# 查看输出确认配置正确
```

6. 设置定时任务 ⏰

为确保生日提醒系统能够每天自动运行，您需要设置一个定时任务（cron job）：

```bash
# 编辑 crontab
crontab -e
```

在打开的编辑器中添加以下行来设置每天上午8点运行脚本：

```bash
# 每天上午8点运行生日提醒脚本
0 8 * * * cd /path/to/birthday_reminder && python3 birthday_reminder.py
```

7. 日志输出（可选）📝

如需保存运行日志以便调试和监控，可以将输出重定向到日志文件：

```bash
# 修改crontab添加日志输出
0 8 * * * cd /path/to/birthday_reminder && python3 birthday_reminder.py >> birthday.log 2>&1
```

这样，所有的标准输出和错误信息都会被记录在 `birthday.log` 文件中。

## 许可证 📄

本项目采用 **[GPL3.0](https://www.gnu.org/licenses/gpl-3.0.en.html#license-text)** 进行许可。你可以免费使用、修改和分发本项目的代码，但必须遵守GPL3.0的许可证条款。如需商业许可，请联系作者ixiaocang@fomail.com。


## 更新日志 📅

- **2025.9.7**
  - 新增部门显示功能和修复年龄计算功能
  - 优化介绍文档索引链接点击异常问题
  - 优化本地部署方案介绍
  - 改进邮件格式为HTML，提升显示效果和多端兼容性

- **2025.9.4**
  - 新增年龄判断和显示功能，重复行跳过
- **2025.8.4**
  - 新增了工作流保活的配置文件，避免60天仓库无提交导致工作流禁用
  - 修复了github actions 控制台返回报错问题
  - 修改介绍文档，优化显示效果
  - 修改许可证为GPL3.0

- **2024.10.17**
  - 修改农历时间及生日判断改为用北京时间判断，避免github运行的时区影响

- **2024.10.16**
  - 修改生日判断改为用北京时间判断，避免github运行的时区影响

- **2024.10.15**
  - 在邮件和后台窗口日志中添加成员生日是属于农历还是公历