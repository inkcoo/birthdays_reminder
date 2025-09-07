###  保持工作流活跃 🔄

为了避免 GitHub Actions 工作流在 60 天无提交时自动禁用，我们需要创建一个定时任务，每天自动提交一个空的 commit。

步骤 1：创建工作流文件

在 GitHub 仓库中创建新文件：
.github/workflows/keep_active.yml


复制[https://raw.githubusercontent.com/inkcoo/birthdays_reminder/main/.github/workflows/keep_active.yml](https://raw.githubusercontent.com/inkcoo/birthdays_reminder/main/.github/workflows/keep_active.yml)代码粘贴到文件中

步骤 2：解决权限问题（处理 403 错误）

在仓库 Settings > Actions > General 页面
找到 "Workflow permissions" 部分
​勾选​ "Read and write permissions"
点击 Save 按钮

步骤 3：启用工作流

提交文件后，转到仓库的 "Actions" 标签页
找到 "Keep Repository Active" 工作流
点击 "Enable workflow"

步骤 4：验证运行

工作流将每30天 UTC 0 点自动运行
或在 Actions 页面手动触发 "Run workflow"
在提交历史中查看空提交："🤖 Keep repository active"
