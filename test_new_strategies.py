"""
测试新的三个策略
"""
import pandas as pd
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from data_manager import DataManager
from strategy import (
    VolumeBreakoutStrategy,
    SteadyTrendStrategy,
    AggressiveMomentumStrategy,
    BalancedMultiFactorStrategy
)
from config import (
    STRATEGY_PARAMS,
    STEADY_TREND_PARAMS,
    AGGRESSIVE_MOMENTUM_PARAMS,
    BALANCED_MULTI_FACTOR_PARAMS
)
from backtest_engine import BacktestEngine
from demo_test_debug import generate_better_mock_data


def test_strategy(strategy_name, strategy_class, params, df):
    """测试单个策略"""
    print(f"\n{'='*60}")
    print(f"测试策略: {strategy_name}")
    print(f"{'='*60}")

    try:
        # 创建策略实例
        strategy = strategy_class(params)

        # 获取交易
        trades = strategy.get_trades(df)

        if not trades:
            print("❌ 未生成任何交易")
            return None

        # 转为DataFrame
        trades_df = pd.DataFrame(trades)

        # 计算统计信息
        total_return = trades_df['收益率%'].sum()
        win_count = len(trades_df[trades_df['收益率%'] > 0])
        loss_count = len(trades_df[trades_df['收益率%'] <= 0])
        win_rate = (win_count / len(trades_df) * 100) if len(trades_df) > 0 else 0

        print(f"✓ 交易数: {len(trades)}")
        print(f"  胜率: {win_rate:.1f}% ({win_count}胜/{loss_count}负)")
        print(f"  总收益: {total_return:.2f}%")
        print(f"  平均收益: {trades_df['收益率%'].mean():.2f}%")
        print(f"  最大收益: {trades_df['收益率%'].max():.2f}%")
        print(f"  最大亏损: {trades_df['收益率%'].min():.2f}%")

        # 显示前5笔交易
        print("\n  前5笔交易:")
        for i, trade in enumerate(trades[:5], 1):
            print(f"    {i}. {trade['买入日期']!s:12} 买入{trade['买入价']:7.2f} "
                  f"-> {trade['卖出日期']!s:12} 卖出{trade['卖出价']:7.2f} "
                  f"收益{trade['收益率%']:6.2f}% [{trade['状态']}]")

        return {
            'strategy_name': strategy_name,
            'trades': len(trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'avg_return': trades_df['收益率%'].mean(),
        }

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("多策略回测系统 - 策略测试")
    print("="*60)

    # 获取数据
    manager = DataManager()
    df = manager.get_data_from_cache('000001')

    # 如果没有缓存数据，使用模拟数据
    if df is None or len(df) == 0:
        print("⚠ 无缓存数据，使用模拟数据进行测试")
        df = generate_better_mock_data('000001', days=250)

    if df is None or len(df) == 0:
        print("❌ 无法获取测试数据")
        return

    print(f"\n数据加载: 000001")
    print(f"  数据量: {len(df)} 行")
    print(f"  日期范围: {df['日期'].min()} ~ {df['日期'].max()}")

    # 测试所有策略
    results = []

    # 1. 原有策略
    result = test_strategy(
        "量能突破回踩策略",
        VolumeBreakoutStrategy,
        STRATEGY_PARAMS,
        df
    )
    if result:
        results.append(result)

    # 2. 稳健型趋势跟踪
    result = test_strategy(
        "稳健型趋势跟踪策略",
        SteadyTrendStrategy,
        STEADY_TREND_PARAMS,
        df
    )
    if result:
        results.append(result)

    # 3. 激进型突破动量
    result = test_strategy(
        "激进型突破动量策略",
        AggressiveMomentumStrategy,
        AGGRESSIVE_MOMENTUM_PARAMS,
        df
    )
    if result:
        results.append(result)

    # 4. 平衡型多因子
    result = test_strategy(
        "平衡型多因子策略",
        BalancedMultiFactorStrategy,
        BALANCED_MULTI_FACTOR_PARAMS,
        df
    )
    if result:
        results.append(result)

    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")

    if results:
        summary_df = pd.DataFrame(results)
        print("\n策略对比:")
        print(summary_df.to_string(index=False))

        # 找最佳策略
        best_return = summary_df.loc[summary_df['total_return'].idxmax()]
        best_winrate = summary_df.loc[summary_df['win_rate'].idxmax()]

        print(f"\n最高收益: {best_return['strategy_name']} ({best_return['total_return']:.2f}%)")
        print(f"最高胜率: {best_winrate['strategy_name']} ({best_winrate['win_rate']:.1f}%)")
    else:
        print("❌ 没有可用的测试结果")


if __name__ == '__main__':
    main()
