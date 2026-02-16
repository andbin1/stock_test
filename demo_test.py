"""演示测试 - 使用模拟数据验证策略逻辑"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine
from config import STRATEGY_PARAMS

def generate_mock_stock_data(symbol: str, days: int = 250) -> pd.DataFrame:
    """生成模拟股票数据"""
    dates = pd.date_range(end=datetime(2025, 2, 13), periods=days, freq='D')

    # 生成有趋势的价格数据
    np.random.seed(hash(symbol) % 2**32)
    trend = np.linspace(0, 5, days)
    noise = np.random.normal(0, 1.5, days)
    prices = 10 + trend + noise

    df = pd.DataFrame({
        '日期': dates,
        '开盘': prices + np.random.uniform(-0.5, 0.5, days),
        '收盘': prices,
        '高': prices + np.random.uniform(0, 2, days),
        '低': prices - np.random.uniform(0, 2, days),
        '成交量': np.random.uniform(100, 500, days) * 1000,  # 万手
        '成交额': prices * np.random.uniform(100, 500, days) * 100,
        '振幅': np.random.uniform(0.5, 3, days),
        '涨跌幅': np.random.uniform(-2, 3, days),
        '涨跌': np.random.uniform(-0.5, 0.5, days),
        '换手率': np.random.uniform(0.5, 3, days),
    })

    return df.sort_values('日期').reset_index(drop=True)


def test_with_mock_data():
    """使用模拟数据进行测试"""
    print("=" * 60)
    print("  演示测试 - 使用模拟数据")
    print("=" * 60)
    print()

    # 生成模拟数据
    symbols = ["mock_000001", "mock_000651", "mock_000858", "mock_600000", "mock_601399"]
    stocks_data = {}

    print("生成模拟股票数据...")
    for symbol in symbols:
        df = generate_mock_stock_data(symbol, days=250)
        stocks_data[symbol] = df
        print(f"  ✓ {symbol}: {len(df)} 天数据")

    print()

    # 运行策略
    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    engine = BacktestEngine()

    print("运行回测...")
    print()

    for symbol, df in stocks_data.items():
        print(f"📊 {symbol}")

        # 计算信号
        signals = strategy.calculate_signals(df)
        trades = strategy.get_trades(df)

        if trades:
            trades_df = pd.DataFrame(trades)

            print(f"   交易数: {len(trades)}")
            print(f"   总收益: {trades_df['收益率%'].sum():.2f}%")
            print(f"   平均收益: {trades_df['收益率%'].mean():.2f}%")

            wins = len(trades_df[trades_df['收益率%'] > 0])
            print(f"   胜率: {wins}/{len(trades)} = {wins/len(trades)*100:.1f}%")

            print(f"   最大收益: {trades_df['收益率%'].max():.2f}%")
            print(f"   最大亏损: {trades_df['收益率%'].min():.2f}%")
            print()

            # 显示前3笔交易
            print("   前3笔交易:")
            for idx, trade in enumerate(trades[:3], 1):
                print(f"     {idx}. {trade['买入日期'].strftime('%Y-%m-%d')} 买 {trade['买入价']:.2f} " +
                      f"→ {trade['卖出日期'].strftime('%Y-%m-%d')} 卖 {trade['卖出价']:.2f} " +
                      f"({trade['收益率%']:+.2f}%)")
        else:
            print("   无交易信号")

        print()

    # 汇总统计
    print("=" * 60)
    print("汇总统计")
    print("=" * 60)

    all_trades = []
    for symbol, df in stocks_data.items():
        signals = strategy.calculate_signals(df)
        trades = strategy.get_trades(df)
        for trade in trades:
            trade['symbol'] = symbol
            all_trades.append(trade)

    if all_trades:
        trades_df = pd.DataFrame(all_trades)
        print(f"\n总交易数: {len(all_trades)}")
        print(f"总收益: {trades_df['收益率%'].sum():.2f}%")
        print(f"平均收益: {trades_df['收益率%'].mean():.2f}%")
        print(f"最高单笔: {trades_df['收益率%'].max():.2f}%")
        print(f"最低单笔: {trades_df['收益率%'].min():.2f}%")

        wins = len(trades_df[trades_df['收益率%'] > 0])
        print(f"胜率: {wins}/{len(all_trades)} = {wins/len(all_trades)*100:.1f}%")

        profits = trades_df[trades_df['收益率%'] > 0]['收益率%']
        losses = trades_df[trades_df['收益率%'] <= 0]['收益率%']

        avg_profit = profits.mean() if len(profits) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        profit_factor = avg_profit / avg_loss if avg_loss > 0 else 0

        print(f"盈亏比: {profit_factor:.2f}")
    else:
        print("\n无任何交易信号")

    print()
    print("✅ 演示测试完成！")
    print()
    print("💡 说明：")
    print("   这是使用模拟数据的测试，用于验证策略逻辑是否正常工作。")
    print("   实际回测需要使用真实的A股数据。")
    print()
    print("下一步建议：")
    print("   1. 修复网络连接问题")
    print("   2. 运行 python main.py 进行完整回测")


if __name__ == "__main__":
    try:
        test_with_mock_data()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
