"""测试交易记录Excel导出功能"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from export_to_excel import export_batch_results_to_excel
from backtest_engine import BacktestEngine
from strategy import VolumeBreakoutStrategy
from config import STRATEGY_PARAMS
from demo_test_debug import generate_better_mock_data
import pandas as pd


def test_excel_export():
    """测试Excel导出功能"""
    print("=" * 60)
    print("测试 Excel 导出功能")
    print("=" * 60)

    # 1. 生成测试数据
    print("\n[1/4] 生成测试数据...")
    test_symbols = ['000001', '600000', '000858']
    all_data = {}

    for symbol in test_symbols:
        df = generate_better_mock_data(symbol)
        all_data[symbol] = df
        print(f"  ✓ {symbol}: {len(df)} 条数据")

    # 2. 运行回测
    print("\n[2/4] 运行回测...")
    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    engine = BacktestEngine()
    results = engine.run_multiple_stocks(all_data, strategy)

    print(f"  ✓ 完成回测 {len(results)} 只股票")
    for symbol, result in results.items():
        print(f"    - {symbol}: {result['num_trades']} 笔交易")

    # 3. 导出Excel
    print("\n[3/4] 导出到Excel...")
    output_file = "test_trades_export.xlsx"
    try:
        export_batch_results_to_excel(results, output_file=output_file)
        print(f"  ✓ 已导出到: {output_file}")
    except Exception as e:
        print(f"  ✗ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 验证文件
    print("\n[4/4] 验证文件...")
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"  ✓ 文件已生成")
        print(f"  ✓ 文件大小: {file_size:.2f} KB")
        print(f"  ✓ 文件路径: {os.path.abspath(output_file)}")
    else:
        print(f"  ✗ 文件不存在: {output_file}")
        return False

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n请打开文件查看: {os.path.abspath(output_file)}")
    print("\nExcel包含以下Sheet:")
    print("  1. 汇总对比 - 所有股票的统计对比")
    print("  2. [股票代码] - 每只股票的详细交易记录")
    print("\n每个交易记录包含:")
    print("  - 序号、买入日期、买入价、卖出日期、卖出价")
    print("  - 持有天数、收益率%（带颜色标记）、状态")

    return True


if __name__ == "__main__":
    success = test_excel_export()
    sys.exit(0 if success else 1)
