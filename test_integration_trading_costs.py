"""
集成测试：交易成本计算与回测引擎

演示完整的交易成本计算流程，从参数配置到回测结果
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backtest_engine import BacktestEngine
from config_manager import ConfigManager
from strategy import VolumeBreakoutStrategy
from config import STRATEGY_PARAMS


def create_sample_data(days=100):
    """创建模拟股票数据"""
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(days)]

    # 生成价格数据（简单上升趋势）
    prices = np.linspace(10, 15, days) + np.random.normal(0, 0.5, days)

    df = pd.DataFrame({
        '日期': dates,
        '开盘': prices,
        '最高': prices + 0.5,
        '最低': prices - 0.5,
        '收盘': prices,
        '成交量': np.random.randint(1000000, 5000000, days),
        '成交额': prices * np.random.randint(1000000, 5000000, days),
    })

    return df


def test_configuration_flow():
    """测试配置流程"""
    print("\n" + "="*70)
    print("步骤1: 配置管理")
    print("="*70)

    config_mgr = ConfigManager()

    # 获取当前交易设置
    settings = config_mgr.get_trading_settings()
    print("\n当前交易设置:")
    print(f"  初始资金: {settings['initial_capital']}元")
    print(f"  交易占比: {settings['position_ratio']}")
    print(f"  手续费率: {settings['commission_rate']}")
    print(f"  滑点: {settings['slippage']}")

    return settings


def test_engine_initialization(settings):
    """测试引擎初始化"""
    print("\n" + "="*70)
    print("步骤2: 初始化回测引擎")
    print("="*70)

    engine = BacktestEngine(
        initial_capital=settings['initial_capital'],
        position_ratio=settings['position_ratio'],
        commission_rate=settings['commission_rate'],
        slippage=settings['slippage']
    )

    print("\n引擎参数:")
    for key, value in engine.backtest_settings.items():
        print(f"  {key}: {value}")

    return engine


def test_position_sizing(engine):
    """测试持仓数量计算"""
    print("\n" + "="*70)
    print("步骤3: 持仓数量计算")
    print("="*70)

    test_prices = [10, 15, 20, 25]
    print("\n不同价格下的持仓数量:")

    for price in test_prices:
        position = engine.calculate_position_size(price)
        cost = price * position
        print(f"  价格{price:3d}元 -> {position:5d}股 -> 成本{cost:,.0f}元")


def test_slippage_impact(engine):
    """测试滑点影响"""
    print("\n" + "="*70)
    print("步骤4: 滑点影响分析")
    print("="*70)

    original_price = 15.0
    buy_price = engine.apply_slippage_to_price(original_price, is_buy=True)
    sell_price = engine.apply_slippage_to_price(original_price, is_buy=False)

    print(f"\n原始价格: {original_price}元")
    print(f"买入价(+{engine.slippage*100:.1f}%滑点): {buy_price:.4f}元")
    print(f"卖出价(-{engine.slippage*100:.1f}%滑点): {sell_price:.4f}元")
    print(f"买卖价差(滑点损耗): {(buy_price - sell_price):.4f}元")


def test_cost_calculation(engine):
    """测试交易成本计算"""
    print("\n" + "="*70)
    print("步骤5: 交易成本计算")
    print("="*70)

    trade_amounts = [50000, 100000, 200000]
    print(f"\n手续费率: {engine.commission_rate*100:.3f}%")

    for amount in trade_amounts:
        cost = engine.calculate_trade_cost(amount)
        cost_rate = (cost / amount) * 100 if amount > 0 else 0
        print(f"  交易额{amount:>7,.0f}元 -> 手续费{cost:>7.2f}元 ({cost_rate:.3f}%)")


def test_complete_trade_cost_application(engine):
    """测试完整交易成本应用"""
    print("\n" + "="*70)
    print("步骤6: 完整交易成本应用")
    print("="*70)

    # 原始交易
    original_trade = {
        '买入日期': '2024-01-15',
        '买入价': 15.0,
        '卖出日期': '2024-01-20',
        '卖出价': 16.0,
        '持有天数': 5,
        '收益率%': 6.67,
        '状态': '平仓',
    }

    print("\n原始交易（未应用成本）:")
    print(f"  买入价: {original_trade['买入价']:.2f}元")
    print(f"  卖出价: {original_trade['卖出价']:.2f}元")
    print(f"  收益率: {original_trade['收益率%']:.2f}%")

    # 应用成本
    trade_with_cost = engine.apply_trading_costs(original_trade)

    print("\n应用成本后:")
    print(f"  买入价(含滑点): {trade_with_cost['买入价']:.4f}元")
    print(f"  卖出价(含滑点): {trade_with_cost['卖出价']:.4f}元")
    print(f"  持仓数量: {trade_with_cost['持仓数量']}股")
    print(f"  买入手续费: {trade_with_cost['买入成本']:.2f}元")
    print(f"  卖出手续费: {trade_with_cost['卖出成本']:.2f}元")
    print(f"  原始收益率: {original_trade['收益率%']:.2f}%")
    print(f"  实际收益率: {trade_with_cost['收益率%']:.2f}%")
    print(f"  成本影响: {trade_with_cost['收益率%'] - original_trade['收益率%']:.2f}%")


def test_backtest_with_costs():
    """测试完整回测流程"""
    print("\n" + "="*70)
    print("步骤7: 完整回测流程")
    print("="*70)

    # 创建数据
    df = create_sample_data(100)

    # 初始化策略和引擎
    strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)

    # 不含成本的回测（传统方式）
    engine_no_cost = BacktestEngine(
        initial_capital=100000,
        position_ratio=0.2,
        commission_rate=0,
        slippage=0
    )

    # 含成本的回测（真实交易）
    engine_with_cost = BacktestEngine(
        initial_capital=100000,
        position_ratio=0.2,
        commission_rate=0.001,
        slippage=0.01
    )

    # 执行回测
    result_no_cost = engine_no_cost.run_single_stock("TEST", df, strategy)
    result_with_cost = engine_with_cost.run_single_stock("TEST", df, strategy)

    print("\n回测结果对比:")
    print(f"\n不含成本的回测:")
    print(f"  交易数: {result_no_cost['num_trades']}")
    print(f"  总收益: {result_no_cost['total_return']:.2f}%")
    print(f"  平均收益: {result_no_cost['avg_return']:.2f}%")
    print(f"  胜率: {result_no_cost['win_rate']:.1f}%")

    print(f"\n含成本的回测:")
    print(f"  交易数: {result_with_cost['num_trades']}")
    print(f"  总收益: {result_with_cost['total_return']:.2f}%")
    print(f"  平均收益: {result_with_cost['avg_return']:.2f}%")
    print(f"  胜率: {result_with_cost['win_rate']:.1f}%")

    if result_no_cost['num_trades'] > 0:
        impact = result_with_cost['total_return'] - result_no_cost['total_return']
        impact_rate = (impact / abs(result_no_cost['total_return'])) * 100 if result_no_cost['total_return'] != 0 else 0
        print(f"\n成本影响:")
        print(f"  收益差值: {impact:.2f}%")
        if result_no_cost['total_return'] != 0:
            print(f"  影响比例: {impact_rate:.1f}%")

    # 显示样本交易
    if result_with_cost['trades']:
        print(f"\n样本交易明细(前3笔):")
        for i, trade in enumerate(result_with_cost['trades'][:3], 1):
            print(f"\n  交易{i}:")
            print(f"    买入: {trade['买入价']:.2f}元 × {trade['持仓数量']}股 = {trade['买入价']*trade['持仓数量']:,.0f}元")
            print(f"    卖出: {trade['卖出价']:.2f}元 × {trade['持仓数量']}股 = {trade['卖出价']*trade['持仓数量']:,.0f}元")
            print(f"    手续费: 买入{trade['买入成本']:.2f}元 + 卖出{trade['卖出成本']:.2f}元 = {trade['买入成本']+trade['卖出成本']:.2f}元")
            print(f"    收益率: {trade['收益率%']:.2f}%")


def main():
    """主测试流程"""
    print("\n" + "="*70)
    print("交易成本计算引擎 - 集成测试")
    print("="*70)

    try:
        # 步骤1: 配置管理
        settings = test_configuration_flow()

        # 步骤2: 引擎初始化
        engine = test_engine_initialization(settings)

        # 步骤3: 持仓数量计算
        test_position_sizing(engine)

        # 步骤4: 滑点影响
        test_slippage_impact(engine)

        # 步骤5: 成本计算
        test_cost_calculation(engine)

        # 步骤6: 完整应用
        test_complete_trade_cost_application(engine)

        # 步骤7: 完整回测
        test_backtest_with_costs()

        print("\n" + "="*70)
        print("✓ 集成测试完成!")
        print("="*70)

        return 0

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
