#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试新策略 - 使用真实数据
"""

from strategy_new import DoubleMACrossStrategy, GridTradingStrategy, TurtleTradingStrategy
from config_new_strategies import (
    DOUBLE_MA_PARAMS,
    GRID_TRADING_PARAMS,
    TURTLE_TRADING_PARAMS
)
from backtest_engine import BacktestEngine
from data_fetcher import get_stock_data

def test_strategy(strategy_name, strategy_class, params, symbol="000001"):
    """测试单个策略"""
    print(f"\n{'='*60}")
    print(f"测试策略：{strategy_name}")
    print(f"{'='*60}")

    # 获取数据
    print(f"获取股票 {symbol} 的数据...")
    df = get_stock_data(symbol, "20240101", "20250213")

    if df is None or len(df) < 50:
        print("❌ 数据获取失败或数据不足")
        return

    # 转换列名（中文->英文）
    df = df.rename(columns={
        '日期': 'date',
        '开盘': 'open',
        '收盘': 'close',
        '高': 'high',
        '低': 'low',
        '成交量': 'volume',
        '成交额': 'amount',
        '涨跌幅': 'pct_change'
    })

    print(f"✅ 数据获取成功：{len(df)} 条记录")
    print(f"   日期范围：{df.iloc[0]['date']} 至 {df.iloc[-1]['date']}")
    print(f"   价格范围：{df['close'].min():.2f} - {df['close'].max():.2f}")

    # 创建策略和引擎
    strategy = strategy_class(params)
    engine = BacktestEngine()

    # 运行回测
    print("\n运行回测...")
    result = engine.run_single_stock(symbol, df, strategy)

    # 显示结果
    print(f"\n回测结果：")
    print(f"  交易次数：{result['num_trades']}")
    print(f"  总收益：{result['total_return']:.2f}%")
    print(f"  平均收益：{result['avg_return']:.2f}%")
    print(f"  胜率：{result['win_rate']:.2f}%")
    print(f"  盈亏比：{result['profit_factor']:.2f}")
    print(f"  最大单笔亏损：{result['max_loss']:.2f}%")

    if result['num_trades'] > 0:
        print(f"\n前5笔交易：")
        trades = result['trades'][:5]
        for i, trade in enumerate(trades, 1):
            print(f"  {i}. {trade['买入日期'][:10]} 买入{trade['买入价']:.2f} → "
                  f"{trade['卖出日期'][:10]} 卖出{trade['卖出价']:.2f} "
                  f"收益{trade['收益率%']:.2f}% ({trade['状态']})")

    return result


def main():
    """主函数"""
    print("\n" + "="*60)
    print("新策略真实数据回测")
    print("="*60)
    print(f"测试股票：000001（平安银行）")
    print(f"回测区间：2024-01-01 至 2025-02-13")

    # 测试所有新策略
    strategies = [
        ("双均线交叉策略", DoubleMACrossStrategy, DOUBLE_MA_PARAMS),
        ("网格交易策略", GridTradingStrategy, GRID_TRADING_PARAMS),
        ("海龟交易法则", TurtleTradingStrategy, TURTLE_TRADING_PARAMS),
    ]

    results = {}
    for name, strategy_class, params in strategies:
        try:
            result = test_strategy(name, strategy_class, params)
            if result:
                results[name] = result
        except Exception as e:
            print(f"❌ 策略测试失败：{e}")
            import traceback
            traceback.print_exc()

    # 总结对比
    if results:
        print(f"\n{'='*60}")
        print("策略对比总结")
        print(f"{'='*60}")
        print(f"{'策略名称':<20} {'交易次数':<8} {'总收益%':<10} {'胜率%':<8} {'盈亏比':<8}")
        print("-" * 60)
        for name, result in results.items():
            print(f"{name:<20} {result['num_trades']:<8} "
                  f"{result['total_return']:<10.2f} "
                  f"{result['win_rate']:<8.2f} "
                  f"{result['profit_factor']:<8.2f}")

        # 找出最佳策略
        best_strategy = max(results.items(), key=lambda x: x[1]['total_return'])
        print(f"\n🏆 最佳策略：{best_strategy[0]} (总收益 {best_strategy[1]['total_return']:.2f}%)")

    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
