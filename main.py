"""主程序 - 快速回测系统"""
import sys
import pandas as pd
from datetime import datetime
from tqdm import tqdm

from config import START_DATE, END_DATE, INDICES, MAX_STOCKS, STRATEGY_PARAMS, INITIAL_CAPITAL
from data_fetcher import get_index_constituents, get_batch_stock_data, get_stock_data
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine
from visualizer import plot_stock_with_signals, plot_results_summary, save_trades_to_csv
from export_to_excel import export_detailed_trades_to_excel, export_batch_results_to_excel


def print_section(title: str):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    print_section("A股交易策略回测系统")
    print(f"回测周期: {START_DATE} ~ {END_DATE}")
    print(f"初始资金: ¥{INITIAL_CAPITAL:,.0f}")
    print(f"策略参数: {STRATEGY_PARAMS}")

    # ========== 步骤1: 获取数据 ==========
    print_section("步骤1: 获取指数成分股和历史数据")

    all_stocks_data = {}

    for index_name, index_code in INDICES.items():
        print(f"\n[{index_name}] 获取成分股...")
        stocks = get_index_constituents(index_code, limit=MAX_STOCKS)

        if stocks:
            print(f"获取 {len(stocks)} 只成分股的历史数据...")
            stocks_data = get_batch_stock_data(stocks, START_DATE, END_DATE)
            all_stocks_data[index_name] = stocks_data
            print(f"成功获取 {len(stocks_data)} 只股票的数据")
        else:
            print(f"[警告] 无法获取 {index_name} 的成分股")

    if not all_stocks_data:
        print("❌ 未能获取任何数据，程序退出")
        return

    # ========== 步骤2: 初始化策略和回测引擎 ==========
    print_section("步骤2: 初始化策略")

    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    engine = BacktestEngine(initial_capital=INITIAL_CAPITAL)

    print(f"✓ 策略: 30均线向上 + 量能放大 + 5日线回踩 + 3日持有")

    # ========== 步骤3: 运行回测 ==========
    print_section("步骤3: 运行回测")

    all_results = {}
    summary_by_index = {}

    for index_name, stocks_data in all_stocks_data.items():
        print(f"\n正在回测 {index_name}...")

        results = engine.run_multiple_stocks(stocks_data, strategy)
        all_results[index_name] = results

        # 聚合结果
        aggregated = BacktestEngine.aggregate_results(results)
        summary_by_index[index_name] = aggregated

        print(f"\n{index_name} 回测结果:")
        print(f"  • 有效股票数: {aggregated['stocks_count']}")
        print(f"  • 总交易数: {aggregated['total_trades']}")
        print(f"  • 总收益: {aggregated['total_return']:.2f}%")
        print(f"  • 平均单笔收益: {aggregated['avg_return_per_trade']:.2f}%")
        print(f"  • 胜率: {aggregated['win_rate']:.1f}%")
        print(f"  • 盈亏比: {aggregated['profit_factor']:.2f}")

    # ========== 步骤4: 汇总对比 ==========
    print_section("步骤4: 指数对比汇总")

    comparison_data = []
    for index_name, summary in summary_by_index.items():
        comparison_data.append({
            '指数': index_name,
            '股票数': summary['stocks_count'],
            '交易数': summary['total_trades'],
            '总收益%': summary['total_return'],
            '平均收益%': summary['avg_return_per_trade'],
            '胜率%': summary['win_rate'],
            '盈亏比': summary['profit_factor'],
        })

    comparison_df = pd.DataFrame(comparison_data)
    print("\n" + comparison_df.to_string(index=False))

    # ========== 步骤5: 导出结果 ==========
    print_section("步骤5: 导出详细结果")

    # 导出汇总对比
    comparison_df.to_csv('回测汇总对比.csv', index=False, encoding='utf-8-sig')
    print("✓ 保存汇总对比到: 回测汇总对比.csv")

    # 导出每个指数的详细交易记录
    for index_name, results in all_results.items():
        detailed_trades = []
        for symbol, result in results.items():
            for trade in result['trades']:
                trade['代码'] = symbol
                detailed_trades.append(trade)

        if detailed_trades:
            detailed_df = pd.DataFrame(detailed_trades)
            filename = f'详细交易记录_{index_name}.csv'
            detailed_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✓ 保存{index_name}详细交易到: {filename}")

    # 导出Excel详细报告
    print("\n📊 正在生成Excel详细报告...")
    try:
        for index_name, results in all_results.items():
            excel_file = f'回测详情_{index_name}.xlsx'
            export_batch_results_to_excel(results, output_file=excel_file)
            print(f"✓ 生成Excel报告: {excel_file}")
    except Exception as e:
        print(f"⚠ Excel导出失败: {e}")

    # ========== 步骤6: 绘制图表 ==========
    print_section("步骤6: 生成图表")

    try:
        # 绘制摘要图表
        for index_name, summary in summary_by_index.items():
            fig = plot_results_summary(summary, index_name)
            fig.savefig(f'回测摘要_{index_name}.png', dpi=150, bbox_inches='tight')
            print(f"✓ 保存摘要图表到: 回测摘要_{index_name}.png")

        # 绘制部分股票的详细图表（前5个有交易的）
        sample_count = 0
        for index_name, results in all_results.items():
            for symbol, result in list(results.items())[:5]:
                if result['num_trades'] > 0:
                    stocks_data = all_stocks_data[index_name]
                    if symbol in stocks_data:
                        df = stocks_data[symbol]
                        strategy_temp = VolumeBreakoutStrategy(STRATEGY_PARAMS)
                        df_signals = strategy_temp.calculate_signals(df)

                        fig = plot_stock_with_signals(df_signals, symbol,
                                                     f"{index_name} - {result['num_trades']}次交易")
                        fig.savefig(f'股票走势_{symbol}.png', dpi=100, bbox_inches='tight')
                        sample_count += 1

        print(f"✓ 保存了 {sample_count} 个股票走势图")

    except Exception as e:
        print(f"⚠ 生成图表时出错: {e}")

    # ========== 完成 ==========
    print_section("✅ 回测完成")
    print("\n📊 生成的文件:")
    print("  • 回测汇总对比.csv - 指数对比结果")
    print("  • 回测详情_*.xlsx - Excel详细报告（包含4个Sheet）")
    print("  • 详细交易记录_*.csv - 每个指数的详细交易")
    print("  • 回测摘要_*.png - 结果摘要图表")
    print("  • 股票走势_*.png - 样本股票走势图")

    print("\n💡 下一步建议:")
    print("  1. 用Excel打开 回测详情_*.xlsx 查看详细交易明细")
    print("  2. 校对每笔交易的买入/卖出时间和价格")
    print("  3. 查看回测汇总对比.csv，了解两个指数的表现")
    print("  4. 修改config.py中的STRATEGY_PARAMS参数，重新运行回测")
    print("  5. 尝试不同的参数组合，找到最优策略")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
