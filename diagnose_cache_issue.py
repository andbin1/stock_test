"""诊断缓存数据问题的脚本"""
import sqlite3
from pathlib import Path
from data_manager import DataManager

print("="*60)
print("缓存数据诊断工具")
print("="*60)
print()

# 1. 检查数据库文件
print("【1】检查数据库文件:")
dm = DataManager()
db_path = Path(dm.db_file)
print(f"  数据库路径: {db_path.absolute()}")
print(f"  文件是否存在: {db_path.exists()}")
if db_path.exists():
    size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"  文件大小: {size_mb:.2f} MB")
print()

# 2. 检查stock_data表
print("【2】检查stock_data表:")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 总记录数
cursor.execute("SELECT COUNT(*) FROM stock_data")
total_records = cursor.fetchone()[0]
print(f"  总记录数: {total_records:,}")

# 股票数量
cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_data")
stock_count = cursor.fetchone()[0]
print(f"  股票数量: {stock_count}")

# 日期范围
cursor.execute("SELECT MIN(date), MAX(date) FROM stock_data")
date_range = cursor.fetchone()
print(f"  日期范围: {date_range[0]} 到 {date_range[1]}")

# 前10只股票
cursor.execute("SELECT DISTINCT symbol FROM stock_data ORDER BY symbol LIMIT 10")
sample_stocks = [row[0] for row in cursor.fetchall()]
print(f"  前10只股票: {', '.join(sample_stocks)}")

conn.close()
print()

# 3. 测试API
print("【3】测试API接口:")
from app_with_cache import app

with app.test_client() as client:
    # 测试get_cached_stocks API
    response = client.get('/api/cache/stocks')
    data = response.get_json()

    print(f"  API状态码: {response.status_code}")
    print(f"  API成功: {data.get('success')}")
    print(f"  API返回总数: {data.get('total')}")
    print(f"  API返回股票列表长度: {len(data.get('stocks', []))}")

    if data.get('success'):
        by_sector = data.get('by_sector', {})
        print(f"  板块分类:")
        for sector, stocks in by_sector.items():
            print(f"    - {sector}: {len(stocks)} 只")
print()

# 4. 测试DataManager
print("【4】测试DataManager:")
all_stocks = dm.get_all_cached_stocks()
print(f"  get_all_cached_stocks() 返回: {len(all_stocks)} 只股票")
if len(all_stocks) > 0:
    print(f"  前10只: {', '.join(all_stocks[:10])}")
print()

# 5. 诊断结论
print("="*60)
print("诊断结论:")
print("="*60)

if stock_count == 0:
    print("❌ 数据库中没有股票数据")
    print("   建议: 在数据管理页面点击'开始获取全部数据'")
elif len(all_stocks) == 0:
    print("❌ DataManager无法读取数据")
    print("   可能原因: 数据库连接问题")
elif not data.get('success'):
    print("❌ API返回失败")
    print(f"   错误信息: {data.get('error')}")
elif data.get('total') == 0:
    print("❌ API返回数据为0")
    print("   可能原因: 板块分类逻辑问题或get_index_constituents调用失败")
else:
    print("✅ 所有检查通过！")
    print(f"   数据库有 {stock_count} 只股票")
    print(f"   API返回 {data.get('total')} 只股票")
    print()
    print("如果前端仍然显示0，可能的原因:")
    print("  1. 浏览器缓存问题 - 尝试硬刷新 (Ctrl+Shift+R)")
    print("  2. JavaScript错误 - 打开浏览器开发者工具(F12)查看Console")
    print("  3. 网络请求失败 - 在开发者工具的Network标签查看API请求")
print()
