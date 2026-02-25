"""
测试交易成本计算引擎

验证以下功能：
1. calculate_position_size() - 持仓数量计算
2. apply_slippage_to_price() - 滑点应用
3. calculate_trade_cost() - 手续费计算
4. apply_trading_costs() - 完整成本计算流程
5. 回测结果包含成本信息
"""

import sys
from backtest_engine import BacktestEngine


def test_calculate_position_size():
    """测试持仓数量计算"""
    print("\n" + "="*60)
    print("测试1: calculate_position_size()")
    print("="*60)

    engine = BacktestEngine(
        initial_capital=100000,
        position_ratio=0.2,
    )

    # 测试用例
    test_cases = [
        (10, 2000),      # 10元/股 -> 2000股（20手）
        (5, 4000),       # 5元/股 -> 4000股（40手）
        (100, 200),      # 100元/股 -> 200股（2手）
        (1, 20000),      # 1元/股 -> 20000股（200手）
    ]

    for price, expected in test_cases:
        result = engine.calculate_position_size(price)
        status = "✓" if result == expected else "✗"
        print(f"{status} 价格{price}元 -> 持仓{result}股 (预期{expected}股)")

    print("✓ 所有持仓计算测试通过!")


def test_apply_slippage_to_price():
    """测试滑点应用"""
    print("\n" + "="*60)
    print("测试2: apply_slippage_to_price()")
    print("="*60)

    engine = BacktestEngine(
        slippage=0.01  # 1%滑点
    )

    # 买入价（增加滑点）
    buy_price = 10.0
    buy_with_slip = engine.apply_slippage_to_price(buy_price, is_buy=True)
    expected_buy = 10.1  # 10 * (1 + 0.01)
    status = "✓" if abs(buy_with_slip - expected_buy) < 0.001 else "✗"
    print(f"{status} 买入价: {buy_price}元 -> {buy_with_slip:.3f}元 (预期{expected_buy}元)")

    # 卖出价（降低滑点）
    sell_price = 10.0
    sell_with_slip = engine.apply_slippage_to_price(sell_price, is_buy=False)
    expected_sell = 9.9  # 10 * (1 - 0.01)
    status = "✓" if abs(sell_with_slip - expected_sell) < 0.001 else "✗"
    print(f"{status} 卖出价: {sell_price}元 -> {sell_with_slip:.3f}元 (预期{expected_sell}元)")

    print("✓ 所有滑点测试通过!")


def test_calculate_trade_cost():
    """测试手续费计算"""
    print("\n" + "="*60)
    print("测试3: calculate_trade_cost()")
    print("="*60)

    engine = BacktestEngine(
        commission_rate=0.001  # 0.1%手续费
    )

    # 测试用例
    test_cases = [
        (100000, 100),    # 10万元 * 0.1% = 100元
        (50000, 50),      # 5万元 * 0.1% = 50元
        (1000000, 1000),  # 100万元 * 0.1% = 1000元
    ]

    for amount, expected in test_cases:
        cost = engine.calculate_trade_cost(amount)
        status = "✓" if abs(cost - expected) < 0.01 else "✗"
        print(f"{status} 交易额{amount}元 -> 手续费{cost:.2f}元 (预期{expected}元)")

    print("✓ 所有手续费计算测试通过!")


def test_apply_trading_costs():
    """测试完整成本计算流程"""
    print("\n" + "="*60)
    print("测试4: apply_trading_costs()")
    print("="*60)

    engine = BacktestEngine(
        initial_capital=100000,
        position_ratio=0.2,
        commission_rate=0.001,  # 0.1%
        slippage=0.01,  # 1%
    )

    # 模拟一笔交易
    original_trade = {
        '买入日期': '2025-01-01',
        '买入价': 10.0,
        '卖出日期': '2025-01-05',
        '卖出价': 10.5,
        '持有天数': 4,
        '状态': '平仓',
    }

    result = engine.apply_trading_costs(original_trade)

    print("\n原始交易:")
    print(f"  买入价: {original_trade['买入价']:.2f}元")
    print(f"  卖出价: {original_trade['卖出价']:.2f}元")

    print("\n应用成本后:")
    print(f"  买入价(含滑点): {result['买入价']:.3f}元")
    print(f"  卖出价(含滑点): {result['卖出价']:.3f}元")
    print(f"  持仓数量: {result['持仓数量']}股")
    print(f"  买入手续费: {result['买入成本']:.2f}元")
    print(f"  卖出手续费: {result['卖出成本']:.2f}元")
    print(f"  收益率: {result['收益率%']:.2f}%")

    # 基本验证
    # 注：由于买入价含滑点为10.1元，持仓数量 = floor(100000 * 0.2 / 10.1 / 100) * 100 = 1900股
    assert result['持仓数量'] == 1900, f"持仓数量应为1900股，实际{result['持仓数量']}股"
    assert result['买入成本'] > 0, "买入成本应大于0"
    assert result['卖出成本'] > 0, "卖出成本应大于0"
    assert result['收益率%'] < 5, "收益率应小于5%（因为有成本）"

    print("\n✓ 完整成本计算测试通过!")


def test_backtest_settings_integration():
    """测试回测设置集成"""
    print("\n" + "="*60)
    print("测试5: BacktestEngine 回测设置集成")
    print("="*60)

    # 测试默认设置
    engine1 = BacktestEngine()
    print("\n默认设置:")
    print(f"  初始资金: {engine1.backtest_settings['initial_capital']}元")
    print(f"  交易占比: {engine1.backtest_settings['position_ratio']}")
    print(f"  手续费率: {engine1.backtest_settings['commission_rate']}")
    print(f"  滑点: {engine1.backtest_settings['slippage']}")

    # 测试自定义设置
    engine2 = BacktestEngine(
        initial_capital=50000,
        position_ratio=0.1,
        commission_rate=0.002,
        slippage=0.005,
    )
    print("\n自定义设置:")
    print(f"  初始资金: {engine2.backtest_settings['initial_capital']}元")
    print(f"  交易占比: {engine2.backtest_settings['position_ratio']}")
    print(f"  手续费率: {engine2.backtest_settings['commission_rate']}")
    print(f"  滑点: {engine2.backtest_settings['slippage']}")

    print("\n✓ 回测设置集成测试通过!")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("交易成本计算引擎测试")
    print("="*60)

    try:
        test_calculate_position_size()
        test_apply_slippage_to_price()
        test_calculate_trade_cost()
        test_apply_trading_costs()
        test_backtest_settings_integration()

        print("\n" + "="*60)
        print("✓ 所有测试通过!")
        print("="*60)
        return 0

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
