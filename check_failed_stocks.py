"""检查失败股票的详细信息"""
import efinance as ef
from data_manager import DataManager
from data_fetcher import get_index_constituents, get_stock_data
from config import START_DATE, END_DATE

print("="*60)
print("失败股票详细分析")
print("="*60)
print()

# 1. 获取已缓存的股票
dm = DataManager()
cached_stocks = set(dm.get_all_cached_stocks())
print(f"✓ 已缓存股票数量: {len(cached_stocks)}")
print()

# 2. 获取尝试过的所有股票代码
all_codes = get_index_constituents("000001", limit=None)  # 沪深A股
print(f"✓ 生成的股票代码总数: {len(all_codes)}")
print()

# 3. 计算失败的股票
failed_codes = [code for code in all_codes if code not in cached_stocks]
print(f"✗ 失败的股票代码数量: {len(failed_codes)}")
print()

# 4. 分析失败原因
print("【失败原因分析】")
print("="*60)

# 按代码段分析
segments = {
    '000': [c for c in failed_codes if c.startswith('000')],
    '300': [c for c in failed_codes if c.startswith('300')],
    '600': [c for c in failed_codes if c.startswith('600')],
    '688': [c for c in failed_codes if c.startswith('688')],
}

for prefix, codes in segments.items():
    if codes:
        percentage = len(codes) / len(failed_codes) * 100
        print(f"{prefix}xxx 段: {len(codes)} 个失败 ({percentage:.1f}%)")

print()

# 5. 测试几个失败的股票
print("【测试失败股票样本】")
print("="*60)
sample_failed = failed_codes[:5]
print(f"测试前5个失败代码: {sample_failed}")
print()

for code in sample_failed:
    try:
        df = ef.stock.get_quote_history(code, beg='20250101', end='20250213')
        if df is None or df.empty:
            print(f"  {code}: ❌ 无数据（可能不存在或已退市）")
        else:
            print(f"  {code}: ✓ 有数据 {len(df)} 条（可能是网络问题）")
    except Exception as e:
        print(f"  {code}: ❌ 错误 - {str(e)[:50]}")

print()

# 6. 推荐操作
print("【建议】")
print("="*60)

success_rate = len(cached_stocks) / len(all_codes) * 100

if success_rate >= 70:
    print("✅ 成功率良好（>70%）")
    print(f"   - 当前成功率: {success_rate:.1f}%")
    print(f"   - 已获取 {len(cached_stocks)} 只股票")
    print(f"   - 足够进行回测分析")
    print()
    print("建议操作：")
    print("1. 直接开始使用回测功能")
    print("2. 失败的代码大多是不存在的股票，无需重试")
elif success_rate >= 50:
    print("⚠️  成功率中等（50-70%）")
    print(f"   - 当前成功率: {success_rate:.1f}%")
    print(f"   - 可能有较多网络超时")
    print()
    print("建议操作：")
    print("1. 检查网络连接")
    print("2. 稍后重试失败的股票")
    print("3. 或者直接使用已获取的数据")
else:
    print("❌ 成功率偏低（<50%）")
    print(f"   - 当前成功率: {success_rate:.1f}%")
    print(f"   - 可能有严重网络问题")
    print()
    print("建议操作：")
    print("1. 检查网络连接")
    print("2. 检查防火墙设置")
    print("3. 尝试更换网络环境")
    print("4. 联系网络管理员")

print()
