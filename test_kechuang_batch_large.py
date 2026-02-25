"""科创板批量数据获取压力测试"""
from data_fetcher import get_index_constituents
from data_manager import DataManager
import time

print("="*60)
print("科创板批量数据获取压力测试")
print("="*60)

# 获取科创板前50只股票
print("\n获取科创板前50只成分股...")
stocks = get_index_constituents("000688", limit=50)
print(f"✓ 获取到 {len(stocks)} 只成分股")
print(f"代码范围: {stocks[0]} ~ {stocks[-1]}")

# 批量获取数据
print("\n开始批量获取数据...")
print(f"预计时间: ~{len(stocks) * 0.5}秒 (每只股票约0.5秒)")

manager = DataManager()
start_time = time.time()

results = manager.batch_fetch_and_cache(stocks, force_refresh=False)

elapsed_time = time.time() - start_time

# 统计结果
success_count = len(results)
fail_count = len(stocks) - success_count
success_rate = (success_count / len(stocks)) * 100

print("\n" + "="*60)
print("测试结果")
print("="*60)
print(f"总计: {len(stocks)} 只股票")
print(f"成功: {success_count} 只")
print(f"失败: {fail_count} 只")
print(f"成功率: {success_rate:.1f}%")
print(f"耗时: {elapsed_time:.1f} 秒")
print(f"平均: {elapsed_time/len(stocks):.2f} 秒/只")

if fail_count > 0:
    failed_stocks = [s for s in stocks if s not in results]
    print(f"\n失败的股票: {failed_stocks[:10]}{'...' if len(failed_stocks) > 10 else ''}")

# 判断测试是否通过
print("\n" + "="*60)
if success_rate >= 95:
    print("✓ 测试通过：成功率 >= 95%")
elif success_rate >= 90:
    print("⚠️  警告：成功率在 90-95% 之间")
else:
    print("✗ 测试失败：成功率 < 90%")

# 检查是否有数据库锁错误
print("\n查看缓存状态...")
status = manager.get_cache_status()
print(f"数据库大小: {status['db_size']:.2f} MB")
print(f"总记录数: {status['total_records']} 条")

# 验证第一只股票不是688000
first_stock = stocks[0]
if first_stock == "688001":
    print(f"\n✓ 验证通过：第一只股票是 {first_stock}")
else:
    print(f"\n✗ 验证失败：第一只股票是 {first_stock}，应该是 688001")

print("="*60)
