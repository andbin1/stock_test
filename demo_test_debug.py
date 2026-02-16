"""演示测试 - 调试版本，显示各个条件的详情"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy import VolumeBreakoutStrategy
from config import STRATEGY_PARAMS

def generate_better_mock_data(symbol: str, days: int = 250) -> pd.DataFrame:
    """生成更符合策略条件的模拟数据 - 包含多个量能突增点"""
    dates = pd.date_range(end=datetime(2025, 2, 13), periods=days, freq='D')
    np.random.seed(hash(symbol) % 2**32)

    # 生成有明显趋势和跳跃的价格
    prices = 10.0
    price_list = []
    volume_list = []
    base_volume = 1000

    for i in range(days):
        # 随机游走，添加向上趋势
        daily_change = np.random.normal(0.15, 1.2)  # 增加趋势
        prices = max(8, prices + daily_change)

        # 多个突增点：每20天有一次量能放大
        if i % 20 == 10:  # 20天周期的第10天
            volume = base_volume * 4.5  # 量能突增4.5倍
        elif i % 20 == 11:  # 第11天也放大（连续2天）
            volume = base_volume * 3.5
        else:
            volume = base_volume * (0.6 + np.random.random())

        price_list.append(prices)
        volume_list.append(volume)

    df = pd.DataFrame({
        '日期': dates,
        '开盘': np.array(price_list) + np.random.uniform(-0.3, 0.3, days),
        '收盘': price_list,
        '高': np.array(price_list) + np.random.uniform(0, 1, days),
        '低': np.array(price_list) - np.random.uniform(0, 1, days),
        '成交量': volume_list,
        '成交额': np.array(price_list) * np.array(volume_list),
        '振幅': np.random.uniform(0.5, 3, days),
        '涨跌幅': np.random.uniform(-2, 3, days),
        '涨跌': np.random.uniform(-0.5, 0.5, days),
        '换手率': np.random.uniform(0.5, 3, days),
    })

    return df.sort_values('日期').reset_index(drop=True)


def test_with_debug():
    """调试测试"""
    print("=" * 80)
    print("  演示测试 - 调试版本")
    print("=" * 80)
    print()

    # 生成单只股票的数据
    symbol = "mock_test"
    df = generate_better_mock_data(symbol)

    print(f"生成模拟数据: {symbol}")
    print(f"  数据点: {len(df)} 天")
    print(f"  价格范围: {df['收盘'].min():.2f} - {df['收盘'].max():.2f}")
    print(f"  成交量范围: {df['成交量'].min():.0f} - {df['成交量'].max():.0f}")
    print()

    # 计算信号
    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
    signals = strategy.calculate_signals(df)

    print("策略参数:")
    print(f"  MA周期: {STRATEGY_PARAMS['ma_period']} 天")
    print(f"  量能倍数: {STRATEGY_PARAMS['volume_multiplier']}x")
    print(f"  持有天数: {STRATEGY_PARAMS['hold_days']} 天")
    print()

    # 查看满足各个条件的数据
    print("条件检查 (最后10行):")
    print()

    condition_df = signals[[
        '日期', '收盘', 'MA5', 'MA30',
        'MA30_Up', 'Volume_Surge', 'MA5_Retest',
        'Buy_Signal', 'Sell_Signal'
    ]].tail(10).copy()

    for col in ['收盘', 'MA5', 'MA30']:
        condition_df[col] = condition_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

    print(condition_df.to_string(index=False))
    print()

    # 统计各条件的触发次数
    print("条件触发统计:")
    print(f"  MA30向上: {signals['MA30_Up'].sum()} 次")
    print(f"  量能放大: {signals['Volume_Surge'].sum()} 次")
    print(f"  5日线回踩: {signals['MA5_Retest'].sum()} 次")
    print(f"  买入信号: {signals['Buy_Signal'].sum()} 次")
    print(f"  卖出信号: {signals['Sell_Signal'].sum()} 次")
    print()

    # 提取交易
    trades = strategy.get_trades(df)

    if trades:
        print(f"交易数: {len(trades)}")
        print()

        trades_df = pd.DataFrame(trades)
        for idx, (i, trade) in enumerate(trades_df.iterrows(), 1):
            print(f"交易 {idx}:")
            print(f"  买入: {trade['买入日期'].strftime('%Y-%m-%d')} @ {trade['买入价']:.2f}")
            print(f"  卖出: {trade['卖出日期'].strftime('%Y-%m-%d')} @ {trade['卖出价']:.2f}")
            print(f"  收益: {trade['收益率%']:+.2f}%")
            print()

        print(f"总统计:")
        print(f"  总收益: {trades_df['收益率%'].sum():.2f}%")
        print(f"  平均收益: {trades_df['收益率%'].mean():.2f}%")
        wins = len(trades_df[trades_df['收益率%'] > 0])
        print(f"  胜率: {wins}/{len(trades)} = {wins/len(trades)*100:.1f}%")
    else:
        print("❌ 无交易信号")
        print()
        print("诊断:")
        print(f"  MA30向上的天数: {signals['MA30_Up'].sum()}")
        print(f"  量能放大的天数: {signals['Volume_Surge'].sum()}")
        print(f"  5日线回踩的天数: {signals['MA5_Retest'].sum()}")
        print()
        print("建议:")
        print("  降低 volume_multiplier (当前: 2.0，尝试 1.5 或 1.0)")


if __name__ == "__main__":
    try:
        test_with_debug()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
