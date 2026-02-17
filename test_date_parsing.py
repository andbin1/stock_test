"""测试日期解析问题"""
import pandas as pd
import sqlite3
from data_manager import DataManager

print("="*60)
print("日期解析测试")
print("="*60)
print()

dm = DataManager()

# 1. 测试从数据库读取所有股票
print("【测试1】获取所有缓存股票...")
try:
    all_stocks = dm.get_all_cached_stocks()
    print(f"  ✓ 成功获取 {len(all_stocks)} 只股票")
except Exception as e:
    print(f"  ✗ 失败: {e}")
print()

# 2. 测试读取几只股票的数据
print("【测试2】测试读取股票数据...")
test_stocks = all_stocks[:5] if len(all_stocks) >= 5 else all_stocks

for symbol in test_stocks:
    try:
        df = dm.get_data_from_cache(symbol)
        if df is not None and len(df) > 0:
            print(f"  ✓ {symbol}: {len(df)} 条记录")
            # 检查日期列
            if '日期' in df.columns:
                date_col = df['日期']
                print(f"      日期范围: {date_col.min()} 到 {date_col.max()}")
                print(f"      日期类型: {date_col.dtype}")
        else:
            print(f"  - {symbol}: 无数据")
    except Exception as e:
        print(f"  ✗ {symbol}: 错误 - {e}")
        import traceback
        traceback.print_exc()
print()

# 3. 测试 API
print("【测试3】测试 /api/cache/stocks API...")
from app_with_cache import app

try:
    with app.test_client() as client:
        response = client.get('/api/cache/stocks')
        data = response.get_json()

        if data.get('success'):
            print(f"  ✓ API成功: total={data.get('total')}")
        else:
            print(f"  ✗ API失败: {data.get('error')}")
except Exception as e:
    print(f"  ✗ API异常: {e}")
    import traceback
    traceback.print_exc()
print()

# 4. 直接测试 pandas 日期解析
print("【测试4】测试各种日期格式...")
test_dates = [
    '2024-01-02',
    '2024/01/02',
    '20240102',
    'XXXX',
    '',
    None,
]

for date_str in test_dates:
    try:
        result = pd.to_datetime(date_str, errors='coerce')
        print(f"  '{date_str}' → {result}")
    except Exception as e:
        print(f"  '{date_str}' → 错误: {e}")
print()

# 5. 检查数据库中的异常数据
print("【测试5】扫描数据库异常数据...")
conn = sqlite3.connect(dm.db_file)
cursor = conn.cursor()

# 检查所有可能有问题的记录
problematic_queries = [
    ("NULL日期", "SELECT COUNT(*) FROM stock_data WHERE date IS NULL"),
    ("空字符串日期", "SELECT COUNT(*) FROM stock_data WHERE date = ''"),
    ("非标准长度", "SELECT COUNT(*) FROM stock_data WHERE LENGTH(date) != 10"),
    ("不包含连字符", "SELECT COUNT(*) FROM stock_data WHERE date NOT LIKE '%-%'"),
]

for desc, query in problematic_queries:
    cursor.execute(query)
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"  ⚠️  {desc}: {count} 条记录")
    else:
        print(f"  ✓ {desc}: 0 条记录")

conn.close()
print()

print("="*60)
print("测试完成")
print("="*60)
