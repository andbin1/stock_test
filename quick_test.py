"""快速测试脚本 - 用于快速验证策略"""
import pandas as pd
from config import STRATEGY_PARAMS, START_DATE, END_DATE
from data_fetcher import get_stock_data
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine


def test_single_stock(symbol: str):
    """测试单个股票"""
    print(f"\n📊 测试股票: {symbol}")
    print(f"   周期: {START_DATE} ~ {END_DATE}")
    print(f"   参数: {STRATEGY_PARAMS}")

    # 获取数据
    df = get_stock_data(symbol, START_DATE, END_DATE)
    if df is None or len(df) < 50:
        print(f"❌ 数据不足或获取失败")
        return None

    # 运行策略
    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    df_signals = strategy.calculate_signals(df)
    trades = strategy.get_trades(df)

    # 打印结果
    print(f"\n📈 交易信号:")
    signal_df = df_signals[df_signals['Buy_Signal'] | df_signals['Sell_Signal']][
        ['日期', '收盘', 'MA5', 'MA30', 'Buy_Signal', 'Sell_Signal']
    ]
    if len(signal_df) > 0:
        print(signal_df.to_string(index=False))
    else:
        print("   无交易信号")

    if trades:
        print(f"\n💰 交易记录:")
        trades_df = pd.DataFrame(trades)
        print(trades_df.to_string(index=False))

        print(f"\n✅ 统计:")
        print(f"   总交易数: {len(trades)}")
        print(f"   总收益: {trades_df['收益率%'].sum():.2f}%")
        print(f"   平均收益: {trades_df['收益率%'].mean():.2f}%")
        print(f"   最大收益: {trades_df['收益率%'].max():.2f}%")
        print(f"   最大亏损: {trades_df['收益率%'].min():.2f}%")
        wins = len(trades_df[trades_df['收益率%'] > 0])
        print(f"   胜率: {wins}/{len(trades)} = {wins/len(trades)*100:.1f}%")
    else:
        print("\n❌ 没有产生任何交易")

    return trades_df if trades else None


if __name__ == "__main__":
    print("=" * 60)
    print("  A股交易策略 - 快速测试")
    print("=" * 60)

    # 测试几个著名的股票
    test_stocks = ["000001", "000651", "000858", "600000", "601399"]

    for stock in test_stocks:
        try:
            test_single_stock(stock)
        except Exception as e:
            print(f"❌ {stock} 测试失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 快速测试完成")
    print("=" * 60)
