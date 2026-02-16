"""使用本地缓存数据进行回测"""
import pandas as pd
from datetime import datetime

from config import START_DATE, END_DATE, INDICES, MAX_STOCKS, STRATEGY_PARAMS, INITIAL_CAPITAL
from data_manager import DataManager
from data_fetcher import get_index_constituents
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine
from export_to_excel import export_batch_results_to_excel

def print_section(title: str):
    """打印分隔符"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def main():
    print_section("A股交易策略回测系统 - 使用本地缓存数据")

    # 初始化数据管理器
    manager = DataManager()

    # ========== 步骤1: 准备数据 ==========
    print_section("步骤1: 准备数据")

    # 获取指数成分股
    index_name = "中证500"
    index_code = INDICES.get(index_name, "000905")

    print(f"📊 获取 {index_name} 成分股...")
    stocks = get_index_constituents(index_code, limit=MAX_STOCKS)

    if not stocks:
        print("❌ 无法获取成分股")
        return

    print(f"✓ 获取到 {len(stocks)} 只成分股")

    # 加载本地缓存数据
    print("\n📂 加载本地缓存数据...")
    all_stocks_data = {}

    for symbol in stocks:
        df = manager.get_data_from_cache(symbol, START_DATE, END_DATE)
        if df is not None and len(df) > 0:
            all_stocks_data[symbol] = df
            print(f"  ✓ {symbol}: 加载 {len(df)} 条数据")
        else:
            print(f"  ✗ {symbol}: 缓存中无数据")

    if not all_stocks_data:
        print("\n⚠️  本地缓存中没有数据！")
        print("\n请先执行以下命令获取数据:")
        print("  python fetch_data_batch.py")
        return

    print(f"\n✓ 成功加载 {len(all_stocks_data)} 只股票的数据")

    # ========== 步骤2: 初始化策略 ==========
    print_section("步骤2: 初始化策略")

    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    engine = BacktestEngine(initial_capital=INITIAL_CAPITAL)

    print(f"✓ 策略: 30均线向上 + 量能放大 + 5日线回踩 + 3日持有")
    print(f"✓ 量能倍数: {STRATEGY_PARAMS['volume_multiplier']}x")

    # ========== 步骤3: 运行回测 ==========
    print_section("步骤3: 运行回测")

    results = engine.run_multiple_stocks(all_stocks_data, strategy)
    aggregated = BacktestEngine.aggregate_results(results)

    print(f"\n{index_name} 回测结果:")
    print(f"  • 有效股票数: {aggregated['stocks_count']}")
    print(f"  • 总交易数: {aggregated['total_trades']}")
    print(f"  • 总收益: {aggregated['total_return']:.2f}%")
    print(f"  • 平均单笔收益: {aggregated['avg_return_per_trade']:.2f}%")
    print(f"  • 胜率: {aggregated['win_rate']:.1f}%")
    print(f"  • 盈亏比: {aggregated['profit_factor']:.2f}")

    # ========== 步骤4: 导出结果 ==========
    print_section("步骤4: 导出结果")

    # 导出汇总
    comparison_df = pd.DataFrame([{
        '指数': index_name,
        '股票数': aggregated['stocks_count'],
        '交易数': aggregated['total_trades'],
        '总收益%': aggregated['total_return'],
        '平均收益%': aggregated['avg_return_per_trade'],
        '胜率%': aggregated['win_rate'],
        '盈亏比': aggregated['profit_factor'],
    }])

    csv_file = f'回测汇总_{index_name}.csv'
    comparison_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"✓ 汇总对比: {csv_file}")

    # 导出详细交易记录
    detailed_trades = []
    for symbol, result in results.items():
        for trade in result['trades']:
            trade['代码'] = symbol
            detailed_trades.append(trade)

    if detailed_trades:
        trades_df = pd.DataFrame(detailed_trades)
        trades_file = f'详细交易_{index_name}.csv'
        trades_df.to_csv(trades_file, index=False, encoding='utf-8-sig')
        print(f"✓ 交易明细: {trades_file}")

    # 导出Excel报告
    try:
        excel_file = f'回测报告_{index_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        export_batch_results_to_excel(results, output_file=excel_file)
        print(f"✓ Excel报告: {excel_file}")
    except Exception as e:
        print(f"⚠️  Excel导出失败: {e}")

    # ========== 步骤5: 显示详细结果 ==========
    print_section("步骤5: 有交易的股票")

    print()
    stock_count = 0
    for symbol, result in sorted(results.items(), key=lambda x: x[1]['total_return'], reverse=True):
        if result['num_trades'] > 0:
            stock_count += 1
            print(f"  {symbol}: {result['num_trades']}笔交易, 总收益 {result['total_return']:+.2f}%, 胜率 {result['avg_return']:.1f}%")

            # 显示具体交易
            for idx, trade in enumerate(result['trades'][:3], 1):
                buy_date = trade['买入日期'].strftime("%Y-%m-%d") if hasattr(trade['买入日期'], 'strftime') else str(trade['买入日期'])
                sell_date = trade['卖出日期'].strftime("%Y-%m-%d") if hasattr(trade['卖出日期'], 'strftime') else str(trade['卖出日期'])
                ret_str = f"{trade['收益率%']:+.2f}%"
                print(f"    交易{idx}: {buy_date} @ {trade['买入价']:.2f} → {sell_date} @ {trade['卖出价']:.2f} ({ret_str})")

    if stock_count == 0:
        print("  无交易信号")

    # ========== 完成 ==========
    print_section("✅ 回测完成")

    print()
    print("📊 生成的文件:")
    print(f"  • 回测汇总_{index_name}.csv")
    if detailed_trades:
        print(f"  • 详细交易_{index_name}.csv")
    print(f"  • 回测报告_{index_name}_*.xlsx")

    print()
    print("💡 下一步:")
    print("  1. 查看Excel报告了解详细交易")
    print("  2. 调整参数后重新回测:")
    print("     - 修改 config.py 中的 STRATEGY_PARAMS")
    print("     - python backtest_with_cache.py")
    print("  3. 更新数据:")
    print("     - python data_manager.py update <symbol>")
    print("     - python fetch_data_batch.py")

    print()
    print("="*70)

if __name__ == "__main__":
    main()
