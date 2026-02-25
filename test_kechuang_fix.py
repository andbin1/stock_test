"""验证科创板修复效果"""
from data_fetcher import get_index_constituents
from data_manager import DataManager

print("="*60)
print("科创板数据下载缓存修复验证")
print("="*60)

# 测试1：检查科创板成分股代码范围
print("\n【测试1】科创板成分股代码范围")
stocks = get_index_constituents("000688", limit=10)
print(f"获取到的前10只股票: {stocks}")
print(f"第一只股票: {stocks[0] if stocks else 'None'}")

if stocks and stocks[0] == "688001":
    print("✓ 修复成功：科创板代码从 688001 开始")
else:
    print("✗ 修复失败：第一只股票不是 688001")

# 测试2：检查数据库超时设置
print("\n【测试2】数据库超时设置")
manager = DataManager()
print(f"数据库超时时间: {manager.db_timeout} 秒")

if manager.db_timeout >= 30:
    print("✓ 修复成功：数据库超时时间已设置")
else:
    print("✗ 修复失败：数据库超时时间未设置")

# 测试3：批量获取测试（小规模）
print("\n【测试3】批量获取科创板数据（5只股票）")
test_stocks = stocks[:5]
print(f"测试股票: {test_stocks}")

results = manager.batch_fetch_and_cache(test_stocks, force_refresh=False)
print(f"\n获取结果: 成功 {len(results)}/{len(test_stocks)} 只")

if len(results) >= len(test_stocks) * 0.8:  # 至少80%成功
    print("✓ 修复成功：批量获取正常工作")
else:
    print("✗ 可能存在问题：成功率低于80%")

print("\n" + "="*60)
print("验证完成")
print("="*60)
