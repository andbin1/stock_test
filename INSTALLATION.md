# Installation Guide

## Python Version Requirements

- **Recommended**: Python 3.8.0+ (stable release)
- **Beta versions**: Python 3.8.0b2 and other beta versions are also supported

If you have Python 3.8.0b2:
- This is a beta testing version of Python 3.8
- The system will work fine with this version
- You may see a version warning - just choose Y to continue

Check your Python version:
```cmd
python --version
```

---

## Three Installation Methods

### Method 1: Interactive Installation (Recommended)

**File**: `install_dependencies.bat`

**Steps**:
1. Double-click `install_dependencies.bat`
2. View your Python version
3. Select a mirror source (1-5), recommend option 1 (Tsinghua)
4. Wait for installation to complete
5. Double-click `start_app.bat` to launch

**Mirror Options**:
1. Tsinghua University (recommended, most stable)
2. Aliyun (alternative)
3. Tencent Cloud (alternative)
4. Douban (alternative)
5. Official PyPI (slow in China)

### Method 2: Quick Installation (One-Click)

**File**: `install_quick.bat`

**Steps**:
1. Double-click `install_quick.bat`
2. Auto-uses Tsinghua mirror
3. Auto-retries with other mirrors on failure
4. Wait for completion
5. Double-click `start_app.bat` to launch

**Features**:
- No user interaction required
- Auto-retry with multiple mirrors
- Fastest and simplest

### Method 3: Manual Command Line (Most Reliable)

**Steps**:

1. Open CMD (Win + R, type `cmd`)

2. Navigate to project directory:
   ```cmd
   cd /d D:\path\to\stock_test
   ```

3. Choose a mirror and install:

   ```cmd
   # Tsinghua (recommended)
   pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

   # Or Aliyun
   pip install -r requirements_release.txt -i https://mirrors.aliyun.com/pypi/simple

   # Or Tencent
   pip install -r requirements_release.txt -i https://mirrors.cloud.tencent.com/pypi/simple
   ```

4. Start application:
   ```cmd
   python app_with_cache.py
   ```

5. Open browser:
   ```
   http://localhost:5000
   ```

---

## China Mirror Sources

### Why use China mirrors?
- Official PyPI is overseas, very slow download
- China mirrors are 10-100x faster
- Reduces download failures

### Recommended Mirrors (in order):

1. **Tsinghua University TUNA** (Best)
   - URL: `https://pypi.tuna.tsinghua.edu.cn/simple`
   - Fast, stable, education network optimized

2. **Aliyun** (Alternative)
   - URL: `https://mirrors.aliyun.com/pypi/simple`
   - Fast, commercial operation

3. **Tencent Cloud** (Alternative)
   - URL: `https://mirrors.cloud.tencent.com/pypi/simple`
   - Fast, nationwide coverage

4. **Douban** (Alternative)
   - URL: `https://pypi.doubanio.com/simple`
   - Veteran mirror, long history

### Set Default Mirror (Optional):

```cmd
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

After setting, all future `pip install` will use Tsinghua mirror automatically.

---

## Troubleshooting

### Issue 1: "Python version might be too old"

**Symptom**: Beta version warning (e.g., Python 3.8.0b2)

**Solution**:
- This is normal, beta versions work fine
- Type Y to continue when prompted
- Or use manual installation method

### Issue 2: Mirror connection timeout

**Symptom**: `[ERROR] Installation failed!`

**Solutions**:
1. Try different mirror: Rerun script, choose another option
2. Check network: Disable VPN/proxy temporarily
3. Use quick install: Run `install_quick.bat` (auto-retry)

### Issue 3: Permission denied

**Symptom**: `Access is denied`

**Solution**: Right-click `.bat` file → "Run as administrator"

### Issue 4: Python not found

**Symptom**: `'python' is not recognized`

**Solutions**:
1. Check if Python is installed
2. Add Python to PATH environment variable
3. Reinstall Python with "Add Python to PATH" checked

### Issue 5: Port 5000 in use

**Symptom**: `Address already in use`

**Solution**:
```cmd
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Or modify port in app_with_cache.py
app.run(debug=False, host='0.0.0.0', port=8080)
```

---

## Verify Installation

```cmd
# Check Python
python --version

# Check dependencies
python -c "import flask, pandas, numpy; print('OK')"

# Test syntax
python -m py_compile app_with_cache.py

# Start app
python app_with_cache.py
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `python --version` | Check Python version |
| `pip list` | List installed packages |
| `python -m pip install --upgrade pip` | Upgrade pip |
| `python app_with_cache.py` | Start application |
| `netstat -ano \| findstr :5000` | Check port 5000 |

---

## Need Help?

- **GitHub**: https://github.com/andbin1/stock_test
- **Issues**: https://github.com/andbin1/stock_test/issues
