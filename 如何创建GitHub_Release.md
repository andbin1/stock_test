# 📦 如何创建 GitHub Release 并上传发布包

## 方式1：使用 GitHub 网页（推荐，最简单）

### 步骤详解

#### 1️⃣ 访问你的仓库

打开浏览器，访问：
```
https://github.com/andbin1/stock_test
```

#### 2️⃣ 创建新的 Release

点击右侧的 **"Releases"** → 点击 **"Create a new release"**

或直接访问：
```
https://github.com/andbin1/stock_test/releases/new
```

#### 3️⃣ 填写 Release 信息

**A. 选择标签（Tag）**
- 点击 "Choose a tag"
- 输入：`v2.1.0`
- 点击 "Create new tag: v2.1.0 on publish"

**B. 填写标题（Release title）**
```
量化回测系统 V2.1 - 正式发布
```

或英文版：
```
Stock Backtest System V2.1 - Official Release
```

**C. 填写说明（Description）**

复制 `RELEASE_NOTES_v2.1.md` 的内容，或使用以下简化版：

```markdown
## 🎉 量化回测系统 V2.1

### 核心特性
- ✅ 4套量化策略（量能突破、稳健趋势、激进动量、平衡多因子）
- ✅ 真实数据源（efinance + akshare）
- ✅ 本地数据缓存
- ✅ Web 可视化界面
- ✅ Excel 详细报告

### 快速开始
1. 下载 `stock_test_v2.1_release.zip`
2. 解压后运行 `install_quick.bat`
3. 运行 `start_app.bat`
4. 浏览器访问 http://localhost:5000

### 系统要求
- Python 3.8+
- Windows 10/11, macOS, Linux

### 更新内容
- ✅ 新增成交金额因子
- ✅ 改进安装脚本（支持多镜像源）
- ✅ 修复股票分类问题
- 🐛 修复多个 Bug

详细说明请查看仓库中的文档。

⚠️ 本系统仅供学习研究使用，不构成投资建议。

---

**如果觉得有用，请给个 ⭐ Star！**
```

#### 4️⃣ 上传发布包

在 **"Attach binaries"** 部分：
- 点击 "Attach files by dragging & dropping, selecting or pasting them"
- 拖拽 `D:\ai_work\stock_test\stock_test_v2.1_release.zip` 到这里
- 或点击选择文件

等待上传完成（文件大小：76KB，很快）

#### 5️⃣ 发布

- 勾选 **"Set as the latest release"**（设为最新版本）
- 点击 **"Publish release"** 按钮

✅ **完成！** 你的 Release 已创建！

---

## 方式2：使用 GitHub CLI（需要安装）

### 安装 GitHub CLI

**Windows**:
```cmd
winget install --id GitHub.cli
```

**Mac**:
```bash
brew install gh
```

**Linux**:
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora/CentOS
sudo dnf install gh
```

### 登录 GitHub

```bash
gh auth login
```

按提示选择：
1. GitHub.com
2. HTTPS
3. Login with a web browser

### 创建 Release

```bash
cd D:\ai_work\stock_test

# 创建 Release 并上传 ZIP
gh release create v2.1.0 ^
  stock_test_v2.1_release.zip ^
  --title "量化回测系统 V2.1 - 正式发布" ^
  --notes-file RELEASE_NOTES_v2.1.md
```

---

## 方式3：使用 Git 命令（仅创建标签）

### 创建标签

```bash
cd D:\ai_work\stock_test

# 创建带注释的标签
git tag -a v2.1.0 -m "Release version 2.1.0"

# 推送标签到远程
git push origin v2.1.0
```

**注意**：这只创建了标签，还需要在 GitHub 网页上手动创建 Release 并上传 ZIP

---

## 📋 Release 信息模板

### 标签（Tag）
```
v2.1.0
```

### 标题（Title）
```
量化回测系统 V2.1 - 正式发布
```

或

```
Stock Backtest System V2.1 - Official Release
```

### 说明（Description）- 简化版

```markdown
## 量化回测系统 V2.1

专业的多策略量化交易回测平台

### 📦 下载与使用

**Windows 用户**：
1. 下载 `stock_test_v2.1_release.zip`
2. 解压后双击 `install_quick.bat`
3. 双击 `start_app.bat`
4. 访问 http://localhost:5000

**Mac/Linux 用户**：
```bash
pip install -r requirements_release.txt
python app_with_cache.py
```

### ✨ 主要特性
- 4套量化策略
- 真实市场数据
- 本地数据缓存
- Web可视化
- Excel导出

### 📋 系统要求
- Python 3.8+
- Windows/Mac/Linux

### 🆕 更新内容
- 新增成交金额因子
- 改进安装脚本
- 修复多个Bug

### ⚠️ 免责声明
仅供学习研究使用，不构成投资建议。

---

**⭐ Star 支持我们！**
```

---

## ✅ 验证 Release

创建成功后，访问：
```
https://github.com/andbin1/stock_test/releases
```

你应该能看到：
- ✅ Release 标题
- ✅ 标签（v2.1.0）
- ✅ 说明内容
- ✅ 附件：stock_test_v2.1_release.zip (76 KB)
- ✅ "Latest" 标签（绿色）

---

## 📊 Release 后的效果

### 用户可以：
1. **直接下载 ZIP**
   ```
   https://github.com/andbin1/stock_test/releases/download/v2.1.0/stock_test_v2.1_release.zip
   ```

2. **查看所有版本**
   ```
   https://github.com/andbin1/stock_test/releases
   ```

3. **使用 wget/curl 下载**
   ```bash
   # wget
   wget https://github.com/andbin1/stock_test/releases/download/v2.1.0/stock_test_v2.1_release.zip

   # curl
   curl -LO https://github.com/andbin1/stock_test/releases/download/v2.1.0/stock_test_v2.1_release.zip
   ```

---

## 🔄 更新 README

在仓库主页的 README.md 中添加下载链接：

```markdown
## 📦 下载

### 稳定版本

**最新版本**：v2.1.0 ([下载](https://github.com/andbin1/stock_test/releases/download/v2.1.0/stock_test_v2.1_release.zip))

查看所有版本：[Releases](https://github.com/andbin1/stock_test/releases)

### 从源码安装

```bash
git clone https://github.com/andbin1/stock_test.git
cd stock_test
pip install -r requirements_release.txt
python app_with_cache.py
```
```

---

## 📝 后续维护

### 发布新版本（如 v2.2.0）

1. **更新代码**
   ```bash
   # 修改代码
   git add .
   git commit -m "Update to v2.2.0"
   git push
   ```

2. **创建新的 Release**
   - 标签：v2.2.0
   - 标题：量化回测系统 V2.2
   - 上传新的 ZIP 文件

3. **更新 Release Notes**
   - 列出新增功能
   - 列出 Bug 修复
   - 更新系统要求

### 版本号规范

采用语义化版本 (Semantic Versioning)：

```
v主版本.次版本.修订号

v2.1.0
│ │ │
│ │ └─ 修订号：Bug修复
│ └─── 次版本：新增功能（向后兼容）
└───── 主版本：重大更新（可能不兼容）
```

示例：
- v2.1.0 → v2.1.1：Bug 修复
- v2.1.0 → v2.2.0：新增功能
- v2.1.0 → v3.0.0：重大更新

---

## 🎯 最佳实践

### Release 说明应包含

- ✅ 版本号和日期
- ✅ 主要功能特性
- ✅ 新增功能列表
- ✅ Bug 修复列表
- ✅ 安装使用说明
- ✅ 系统要求
- ✅ 免责声明
- ✅ 下载链接

### 不要

- ❌ 在 Release 中包含开发版本
- ❌ 上传超大文件（>100MB）
- ❌ 修改已发布的 Release（创建新版本）
- ❌ 删除旧版本（保留历史）

---

## 💡 提示

1. **Release 文件不占用仓库空间**
   - Git 仓库大小不会增加
   - Release 文件存储在 GitHub 的 CDN 上

2. **可以后期编辑 Release**
   - 可以修改说明
   - 可以添加/删除附件
   - 但不推荐修改已发布的版本

3. **统计下载数据**
   - GitHub 自动统计下载次数
   - 在 Release 页面可以看到

---

**现在就去创建你的第一个 Release 吧！** 🚀
