"""检查科创板有效股票代码"""
from data_fetcher import get_stock_data
import time

test_codes = [
    '688001', '688014', '688024', '688034', '688040',
    '688050', '688100', '688200', '688500', '688700'
]

print("检查科创板股票代码有效性:")
print("="*60)

valid = []
invalid = []

for code in test_codes:
    df = get_stock_data(code, '20240101', '20250213')
    if df is not None and len(df) > 0:
        valid.append(code)
        print(f"✓ {code}: 有效 ({len(df)}条数据)")
    else:
        invalid.append(code)
        print(f"✗ {code}: 无效或无数据")
    time.sleep(0.3)

print("\n" + "="*60)
print(f"有效股票: {len(valid)} 只")
print(f"无效股票: {len(invalid)} 只")
print(f"\n无效代码列表: {invalid}")
print("\n说明: 科创板并非所有代码都有对应股票，这是正常现象")
print("      系统会自动跳过无效代码，不影响其他股票的数据获取")
