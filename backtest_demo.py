"""快速演示回测 - 使用少量股票快速验证系统"""
import pandas as pd
from datetime import datetime

from config import START_DATE, END_DATE, INDICES, MAX_STOCKS, STRATEGY_PARAMS, INITIAL_CAPITAL
from data_fetcher import get_index_constituents, get_batch_stock_data
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine
from export_to_excel import export_batch_results_to_excel

print("=" * 80)
print("  A股交易策略 - 快速演示回测")
print("=" * 80)
print()

# 只测试成功获取数据的几只股票
demo_stocks = ["000001", "000651", "000858", "600000", "600016"]

print(f"使用演示股票进行快速回测: {', '.join(demo_stocks)}")
print(f"回测周期: {START_DATE} ~ {END_DATE}")
print()

# 获取数据
print("正在获取数据...")
stocks_data = get_batch_stock_data(demo_stocks, START_DATE, END_DATE)

if not stocks_data:
    print("❌ 无法获取任何数据")
    exit(1)

print(f"✓ 成功获取 {len(stocks_data)} 只股票的数据")
print()

# 运行回测
print("正在运行回测...")
strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
engine = BacktestEngine(initial_capital=INITIAL_CAPITAL)

results = engine.run_multiple_stocks(stocks_data, strategy)

# 聚合结果
aggregated = BacktestEngine.aggregate_results(results)

print()
print("=" * 80)
print("回测结果")
print("=" * 80)
print()

print(f"回测股票: {len(results)}")
print(f"总交易数: {aggregated['total_trades']}")
print(f"总收益: {aggregated['total_return']:.2f}%")
print(f"平均单笔收益: {aggregated['avg_return_per_trade']:.2f}%")
print(f"胜率: {aggregated['win_rate']:.1f}%")
print(f"盈亏比: {aggregated['profit_factor']:.2f}")
print()

# 显示每只股票的结果
print("各股票详细结果:")
print()

for symbol, result in results.items():
    if result['num_trades'] > 0:
        print(f"  {symbol}: {result['num_trades']}笔交易, 总收益{result['total_return']:+.2f}%, 胜率{result['avg_return']:.2f}%")

print()
print("=" * 80)

# 导出 Excel
print("正在导出Excel...")

try:
    excel_file = f'演示回测_结果.xlsx'
    export_batch_results_to_excel(results, output_file=excel_file)
    print(f"✓ 已导出到: {excel_file}")
except Exception as e:
    print(f"⚠ Excel导出失败: {e}")

print()
print("✅ 演示回测完成!")
