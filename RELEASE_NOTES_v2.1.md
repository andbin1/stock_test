# 量化回测系统 V2.1 发布说明

> Release Date: 2025-02-17

## 🎉 主要特性

### 核心功能
- ✅ **4套量化策略** - 量能突破、稳健趋势、激进动量、平衡多因子
- ✅ **真实数据源** - 接入 efinance 和 akshare API
- ✅ **智能缓存** - 本地 SQLite 数据库，支持增量更新
- ✅ **多板块回测** - 支持沪深A股、创业板、科创板、中证500等
- ✅ **Web可视化** - 简洁直观的操作界面
- ✅ **Excel导出** - 详细的交易记录和统计报告

### 技术栈
- Python 3.8+
- Flask 2.3.2
- pandas, numpy
- SQLite
- efinance, akshare

---

## 📦 下载与安装

### Windows 用户（推荐）

**快速开始**（3步）：

1. 下载 `stock_test_v2.1_release.zip` 并解压
2. 双击运行 `install_quick.bat`（一键安装依赖）
3. 双击运行 `start_app.bat`（启动应用）
4. 浏览器访问 `http://localhost:5000`

**详细步骤**：

```
第1步：下载并解压
   下载本页面下方的 stock_test_v2.1_release.zip
   解压到任意目录

第2步：安装依赖
   方式A：双击 install_quick.bat（推荐，自动安装）
   方式B：双击 install_dependencies.bat（可选择镜像源）
   方式C：命令行安装
      cd 解压目录
      pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

第3步：启动应用
   双击 start_app.bat
   或命令行：python app_with_cache.py

第4步：使用系统
   浏览器打开 http://localhost:5000
   查看"用户使用手册.md"了解详细功能
```

### Mac/Linux 用户

```bash
# 1. 下载并解压
unzip stock_test_v2.1_release.zip
cd stock_test_v2.1_release

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# 3. 安装依赖
pip install -r requirements_release.txt

# 4. 启动应用
python app_with_cache.py

# 5. 访问应用
# 浏览器打开 http://localhost:5000
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/andbin1/stock_test.git
cd stock_test

# 安装依赖
pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动应用
python app_with_cache.py
```

---

## 📋 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11, macOS, Linux |
| Python | 3.8.0+ (支持 beta 版本如 3.8.0b2) |
| 内存 | 建议 4GB+ |
| 硬盘 | 建议 1GB+ 可用空间 |
| 网络 | 首次运行需要联网下载数据 |

---

## 🎯 快速使用

### 1. 获取数据
- 点击"数据管理"标签
- 选择板块（如"创业板"）
- 点击"批量获取数据"
- 等待数据下载完成

### 2. 运行回测
- 点击"回测模块"标签
- 选择回测模式（全部/板块/手动）
- 选择策略（4套可选）
- 点击"运行回测"

### 3. 查看结果
- 查看回测报告（收益率、夏普比率、最大回撤等）
- 点击"导出Excel"获取详细交易记录

---

## 📊 策略说明

| 策略 | 特点 | 交易频率 | 风险 | 适用市场 |
|------|------|----------|------|----------|
| **量能突破回踩** | 经典基础策略 | 中等 | 中低 | 全市场 |
| **稳健趋势跟随** | 低频严格风控 | 低 | 低 | 蓝筹股 |
| **激进动量突破** | 高频快进快出 | 高 | 高 | 创业板/科创板 |
| **平衡多因子** | 多维度评分 | 中等 | 中 | 中证500 |

详细策略说明请查看 `STRATEGY_GUIDE.md`

---

## 🔧 常见问题

### Q1: 安装依赖失败？

**解决方案**：
```cmd
# 使用国内镜像源
pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用快速安装脚本
双击运行 install_quick.bat（自动重试多个镜像源）
```

### Q2: 提示 Python 版本问题？

**解决方案**：
- 如果你使用的是 Python 3.8.0b2（beta版），可以正常使用
- 看到版本警告时，输入 Y 继续即可
- 或使用 Python 3.8.0 正式版

### Q3: 启动失败，端口被占用？

**解决方案**：
```cmd
# 查看端口占用
netstat -ano | findstr :5000

# 关闭占用的进程
taskkill /PID <进程号> /F

# 或修改端口（编辑 app_with_cache.py）
app.run(debug=False, host='0.0.0.0', port=8080)
```

### Q4: 数据获取失败？

**可能原因**：
- 网络连接问题
- API 限流
- 股票代码错误

**解决方案**：
- 检查网络连接
- 降低并发数量
- 稍后重试

更多问题请查看 `安装说明.txt` 或提交 Issue

---

## 📚 文档

- **README.md** - 项目说明
- **用户使用手册.md** - 详细使用教程
- **安装说明.txt** - 完整安装指南（中文）
- **INSTALLATION.md** - Installation guide (English)
- **STRATEGY_GUIDE.md** - 策略详细说明
- **解决方案-安装脚本乱码.md** - 编码问题解决

---

## 🆕 V2.1 更新内容 (2025-02-17)

### 新增功能
- ✅ 成交金额因子过滤（turnover_min/max）
- ✅ 改进版安装脚本（支持 beta 版本 Python）
- ✅ 5个国内镜像源可选
- ✅ 快速安装脚本（install_quick.bat）
- ✅ 自动重试机制

### 优化改进
- ✅ 优化股票分类逻辑（修复板块统计错误）
- ✅ 修复批量获取性能问题
- ✅ 改进错误处理机制
- ✅ 增强脚本跨系统兼容性

### Bug 修复
- 🐛 修复 generate_stock_codes() 参数错误
- 🐛 修复缓存股票数量显示不正确
- 🐛 修复中文脚本编码乱码问题
- 🐛 修复 Python beta 版本检测问题

---

## 📈 性能指标（示例）

**回测条件**：
- 策略：量能突破回踩
- 周期：2024-01-01 至 2025-02-13
- 股票池：创业板 300只

**回测结果**：
```
📈 总收益率：        35.42%
💰 年化收益率：      18.23%
📉 最大回撤：        -12.5%
📊 夏普比率：        1.45
🎯 胜率：            62.3%
📈 盈亏比：          2.1:1
🔄 交易次数：        128 次
```

*注：回测结果仅供参考，不构成投资建议*

---

## ⚠️ 免责声明

**本系统仅供学习和研究使用，不构成任何投资建议。**

- 回测结果不代表未来实际收益
- 实盘交易存在滑点、手续费等额外成本
- 历史数据不能完全预测市场走势
- 投资有风险，入市需谨慎

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 联系方式

- **GitHub**: https://github.com/andbin1/stock_test
- **Issues**: https://github.com/andbin1/stock_test/issues

---

## 🙏 致谢

感谢以下开源项目：
- Flask - Web 框架
- pandas - 数据处理
- efinance - 股票数据
- akshare - 金融数据

---

**如果觉得有用，请给个 ⭐ Star！**

**Happy Trading! 📈**
