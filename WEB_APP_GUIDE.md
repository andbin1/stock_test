# 📱 Web应用使用指南

## 概述

本项目已转换为**Web应用**，支持在任何设备（包括Android手机）的浏览器中使用。

不需要打包成原生APK，直接通过浏览器访问Web界面。

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements_web.txt
```

### 2. 启动服务
```bash
python app.py
```

输出示例：
```
 * Running on http://0.0.0.0:5000
```

### 3. 在浏览器访问

**同一台电脑**：
```
http://localhost:5000
```

**同一局域网（Android手机）**：
```
http://[PC_IP_ADDRESS]:5000
```

**查看PC的IP地址**：
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```

---

## 📲 在Android手机上使用

### 步骤1：连接到同一WiFi
- 确保手机和电脑在同一WiFi网络

### 步骤2：获取PC的IP地址
在电脑上运行：
```bash
ipconfig
```

找到类似 `192.168.x.x` 的IPv4地址

### 步骤3：在手机浏览器打开
在Android手机的任何浏览器中输入：
```
http://192.168.x.x:5000
```

---

## 🌍 远程访问（云服务器部署）

### 选项1：使用Heroku（免费）

1. 注册 Heroku 账号：https://www.heroku.com/

2. 创建文件 `Procfile`：
```
web: gunicorn app:app
```

3. 部署：
```bash
heroku login
heroku create your-app-name
git push heroku main
```

访问：`https://your-app-name.herokuapp.com`

### 选项2：使用PythonAnywhere（免费）

1. 上传代码到 PythonAnywhere
2. 配置WSGI应用指向 `app:app`
3. 启动Web应用
4. 访问 `your-username.pythonanywhere.com`

### 选项3：使用Streamlit Cloud（推荐简单）

创建 `streamlit_app.py`：
```python
import streamlit as st
from demo_test_debug import generate_better_mock_data
from strategy import VolumeBreakoutStrategy
from config import STRATEGY_PARAMS

st.set_page_config(page_title="A股回测系统", layout="wide")

st.title("📈 A股交易策略回测")

stock_code = st.text_input("股票代码", "000001")

if st.button("运行回测"):
    df = generate_better_mock_data(stock_code)
    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    trades = strategy.get_trades(df)

    st.write(f"交易笔数: {len(trades)}")
    st.dataframe(pd.DataFrame(trades))
```

部署：在 https://streamlit.io/ 连接GitHub并部署

---

## 🎯 功能介绍

### Web界面功能

1. **显示策略参数**
   - MA周期、量能倍数、持有天数等

2. **输入股票代码**
   - 支持任何A股代码（如 000001, 600000 等）

3. **运行回测**
   - 即时运行演示回测
   - 显示买卖信号统计
   - 展示所有交易明细

4. **导出Excel**
   - 下载详细的Excel报告
   - 包含4个Sheet：交易摘要、交易清单、信号详情、策略参数

---

## 📊 API文档

### POST /api/backtest/demo
运行演示回测

**请求**：
```json
{
  "stock_code": "000001"
}
```

**响应**：
```json
{
  "success": true,
  "stock_code": "000001",
  "trades": 5,
  "total_return": 2.45,
  "avg_return": 0.49,
  "win_rate": 80.0,
  "trades_list": [...]
}
```

### GET /api/config
获取策略参数

### POST /api/backtest/export
导出为Excel文件

---

## 🔧 配置修改

### 修改策略参数

编辑 `config.py`：
```python
STRATEGY_PARAMS = {
    "ma_period": 30,          # 30日均线
    "volume_multiplier": 3.0, # 量能倍数
    "hold_days": 3,           # 持有天数
}
```

保存后，刷新Web页面即可看到新参数。

---

## 💻 生产环境部署

### 使用Gunicorn（推荐）

```bash
# 安装gunicorn
pip install gunicorn

# 运行（4个worker，监听所有IP）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用Docker

创建 `Dockerfile`：
```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements_web.txt .
RUN pip install -r requirements_web.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行：
```bash
docker build -t stock-backtest .
docker run -p 5000:5000 stock-backtest
```

---

## 🔒 安全建议

1. **生产环境改用HTTPS**
   ```bash
   # 使用Let's Encrypt
   certbot certonly --standalone -d your-domain.com
   ```

2. **添加认证**
   - 修改 `app.py` 添加用户认证

3. **限制并发请求**
   - 使用 `gunicorn --workers` 控制

4. **数据库持久化**
   - 目前使用内存存储结果
   - 生产环境建议使用Redis或数据库

---

## 📱 移动App方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Web应用** ⭐ | 无需编译、易维护、跨平台 | 需要网络 |
| APK原生应用 | 离线使用、性能好 | 复杂、难维护、库支持差 |
| PWA (Progressive Web App) | 可离线、App感受 | 不支持某些功能 |

**建议**：优先使用Web应用，用户体验最佳。

---

## 🆘 故障排查

### 问题1：无法从手机访问
**解决**：
```bash
# 检查防火墙是否阻止5000端口
# Windows: 允许Python通过防火墙
# 检查PC和手机是否在同一WiFi
# 检查IP地址是否正确
```

### 问题2：数据获取失败
**原因**：efinance/akshare无法连接
**解决**：
- 使用演示数据（已启用）
- 配置代理/VPN
- 部署到有外网的云服务器

### 问题3：Excel导出失败
**解决**：
```bash
# 检查openpyxl是否已安装
pip install openpyxl
```

---

## 📈 性能优化

1. **增加Worker数**
   ```bash
   gunicorn -w 8 -b 0.0.0.0:5000 app:app
   ```

2. **启用缓存**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

3. **数据库连接池**
   - 部署到生产时使用

---

## 🎓 下一步改进

- [ ] 添加用户认证和历史保存
- [ ] 实时数据推送（WebSocket）
- [ ] 参数自动优化（AI/ML）
- [ ] 多策略支持
- [ ] 与真实交易平台对接

---

## 📞 联系支持

有问题？
1. 查看此文档
2. 检查浏览器控制台错误（F12）
3. 查看服务器日志

---

**总结**：Web应用是最佳方案，支持所有设备（Android、iOS、Web），无需打包、易维护、用户体验好。
