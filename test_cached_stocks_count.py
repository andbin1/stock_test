"""测试缓存股票数量是否正确"""
from data_manager import DataManager
from data_fetcher import get_index_constituents

# 初始化数据管理器
manager = DataManager()

# 获取数据库中的股票
all_stocks = manager.get_all_cached_stocks()
print(f"✓ 数据库中实际股票数量: {len(all_stocks)}")

# 模拟API分类逻辑
by_sector = {
    '沪深A股': [],
    '创业板': [],
    '科创板': [],
    '深成指': [],
    '中证500': [],
    '其他': []
}

# 提前获取中证500列表（只调用一次）
zz500_set = set()
try:
    zz500_list = get_index_constituents('000905', limit=None)
    zz500_set = set(zz500_list)
    print(f"✓ 中证500列表生成完成: {len(zz500_set)} 只")
except Exception as e:
    print(f"✗ 获取中证500列表失败: {e}")

def categorize_stock(symbol: str, zz500_stocks: set) -> list:
    """返回股票所属的所有板块"""
    sectors = []

    # 创业板：300开头
    if symbol.startswith('300'):
        sectors.extend(['创业板', '深成指', '沪深A股'])
    # 科创板：688开头
    elif symbol.startswith('688'):
        sectors.extend(['科创板', '沪深A股'])
    # 深圳主板：000/001/002/003/004开头
    elif symbol.startswith(('000', '001', '002', '003', '004')):
        sectors.extend(['深成指', '沪深A股'])
    # 上海主板：6开头
    elif symbol.startswith('6'):
        sectors.append('沪深A股')
    else:
        sectors.append('其他')

    # 检查是否属于中证500
    if symbol in zz500_stocks:
        sectors.append('中证500')

    return sectors

# 分类股票
classified_count = 0
for stock in all_stocks:
    sectors = categorize_stock(stock, zz500_set)
    for sector in sectors:
        if sector in by_sector:
            by_sector[sector].append(stock)
    classified_count += 1

# 去重并排序
for sector in by_sector:
    by_sector[sector] = sorted(list(set(by_sector[sector])))

# 移除空的板块
by_sector = {k: v for k, v in by_sector.items() if v}

print(f"\n✓ 分类完成，共处理 {classified_count} 只股票")
print(f"\n各板块股票数量:")
for sector, stocks in sorted(by_sector.items()):
    print(f"  {sector}: {len(stocks)} 只")

# 验证总数
total_unique = len(set([s for stocks in by_sector.values() for s in stocks]))
print(f"\n✓ 分类后唯一股票总数: {total_unique}")

if total_unique == len(all_stocks):
    print(f"✅ 测试通过！所有 {len(all_stocks)} 只股票都已正确分类")
else:
    print(f"⚠️ 警告：数据库有 {len(all_stocks)} 只，但分类后只有 {total_unique} 只")
    missing = len(all_stocks) - total_unique
    print(f"   可能有 {missing} 只股票未被分类")
