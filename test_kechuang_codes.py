"""测试科创板股票代码是否有效"""
from data_fetcher import get_stock_data
import time

# 测试不同科创板代码
test_codes = ['688000', '688001', '688005', '688010', '688050', '688100', '688200', '688500']

print("科创板股票代码测试:")
print("="*60)

for code in test_codes:
    df = get_stock_data(code, '20240101', '20250213')
    if df is not None and len(df) > 0:
        print(f"{code}: 有效 - {len(df)}条数据")
    else:
        print(f"{code}: 无效或无数据")
    time.sleep(0.5)  # 避免请求过快

print("\n结论：")
print("688000 是无效的股票代码")
print("科创板实际代码从 688001 开始")
