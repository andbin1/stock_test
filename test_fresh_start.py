"""从零开始测试完整流程"""
import os
from pathlib import Path
from data_manager import DataManager
from data_fetcher import get_stock_data
from config import START_DATE, END_DATE

print("="*60)
print("从零开始测试 - 完整流程")
print("="*60)
print()

# 1. 检查数据库是否已删除
db_file = Path("data_cache/stock_data.db")
print(f"【步骤1】检查数据库状态:")
print(f"  数据库文件: {db_file}")
print(f"  是否存在: {db_file.exists()}")
if db_file.exists():
    size_mb = db_file.stat().st_size / (1024 * 1024)
    print(f"  文件大小: {size_mb:.2f} MB")
print()

# 2. 初始化数据管理器（会创建新数据库）
print("【步骤2】初始化数据管理器...")
dm = DataManager()
print(f"  ✓ 数据管理器已初始化")
print(f"  ✓ 数据库已创建: {db_file.exists()}")
print()

# 3. 获取测试股票数据
test_stocks = ['000001', '600000', '300001']
print(f"【步骤3】获取测试股票数据: {test_stocks}")
print()

for symbol in test_stocks:
    print(f"  测试 {symbol}...")
    try:
        # 从网络获取数据
        df = dm.fetch_and_cache(symbol, START_DATE, END_DATE, force_refresh=True)

        if df is not None and len(df) > 0:
            print(f"    ✓ 成功获取 {len(df)} 条记录")
            print(f"    ✓ 日期范围: {df['日期'].min()} 到 {df['日期'].max()}")
        else:
            print(f"    ✗ 获取失败或无数据")
    except Exception as e:
        print(f"    ✗ 异常: {e}")
        import traceback
        traceback.print_exc()
    print()

# 4. 验证数据库中的数据
print("【步骤4】验证数据库...")
all_stocks = dm.get_all_cached_stocks()
print(f"  ✓ 缓存股票数量: {len(all_stocks)}")
print(f"  ✓ 股票列表: {all_stocks}")
print()

# 5. 测试从缓存读取
print("【步骤5】测试从缓存读取数据...")
for symbol in all_stocks[:3]:  # 测试前3只
    try:
        df = dm.get_data_from_cache(symbol)
        if df is not None and len(df) > 0:
            print(f"  ✓ {symbol}: {len(df)} 条记录")
        else:
            print(f"  - {symbol}: 无数据")
    except Exception as e:
        print(f"  ✗ {symbol}: 错误 - {e}")
print()

# 6. 测试 API
print("【步骤6】测试 /api/cache/stocks API...")
from app_with_cache import app

try:
    with app.test_client() as client:
        response = client.get('/api/cache/stocks')
        print(f"  状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"  Success: {data.get('success')}")

            if data.get('success'):
                print(f"  ✓ Total: {data.get('total')}")
                print(f"  ✓ Stocks: {len(data.get('stocks', []))}")
                print(f"  ✓ By sector keys: {list(data.get('by_sector', {}).keys())}")
            else:
                print(f"  ✗ Error: {data.get('error')}")
        else:
            print(f"  ✗ HTTP错误: {response.status_code}")
except Exception as e:
    print(f"  ✗ API异常: {e}")
    import traceback
    traceback.print_exc()
print()

# 7. 检查数据库大小
print("【步骤7】检查数据库文件...")
if db_file.exists():
    size_mb = db_file.stat().st_size / (1024 * 1024)
    print(f"  ✓ 文件大小: {size_mb:.2f} MB")
else:
    print(f"  ✗ 数据库文件不存在")
print()

# 8. 总结
print("="*60)
print("测试完成 - 总结")
print("="*60)
if len(all_stocks) > 0:
    print(f"✅ 成功测试！")
    print(f"   - 获取了 {len(all_stocks)} 只股票数据")
    print(f"   - 数据库文件大小: {size_mb:.2f} MB")
    print(f"   - API 工作正常")
    print()
    print("下一步: 打开浏览器测试前端")
    print("  1. 启动应用: python app_with_cache.py")
    print("  2. 访问: http://localhost:5000")
    print("  3. 点击'回测'标签页")
    print("  4. 点击'刷新'按钮")
    print(f"  5. 应该显示: 已缓存 {len(all_stocks)} 只股票数据")
else:
    print(f"❌ 测试失败！")
    print(f"   - 未能获取任何股票数据")
    print(f"   - 请检查网络连接和 efinance 库")
print()
