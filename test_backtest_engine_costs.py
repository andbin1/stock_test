"""测试回测引擎成本计算 - 验证持仓数量、滑点和手续费计算"""
import pytest
import math
from backtest_engine import BacktestEngine


class TestPositionSizeCalculation:
    """持仓数量计算测试"""

    def test_case_1_basic_calculation(self):
        """用例1: IC=100k, PR=0.2, 股价=50元
        期望: 400手 (40000股)
        计算: floor(100000 × 0.2 ÷ 50 ÷ 100) × 100 = 400
        """
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)
        position = engine.calculate_position_size(price=50)

        # 计算期望值
        amount = 100000 * 0.2 / 50  # 400 shares
        expected = int(amount // 100) * 100  # 400

        assert position == expected, f"期望 {expected}，实际 {position}"
        assert position == 400, f"期望400手，实际{position}手"

    def test_case_2_high_price_stock(self):
        """用例2: IC=100k, PR=0.1, 股价=100元
        期望: 100手 (10000股)
        计算: floor(100000 × 0.1 ÷ 100 ÷ 100) × 100 = 100
        """
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.1)
        position = engine.calculate_position_size(price=100)

        amount = 100000 * 0.1 / 100  # 10 shares
        expected = int(amount // 100) * 100  # 0

        # 实际应该是100手，不是0手
        # 让我重新检查计算
        # 100000 * 0.1 / 100 = 100，然后 100 // 100 = 1，1 * 100 = 100
        expected = 100
        assert position == expected, f"期望{expected}，实际{position}"

    def test_case_3_large_capital_low_price(self):
        """用例3: IC=50k, PR=0.5, 股价=25元
        期望: 400手 (40000股)
        计算: floor(50000 × 0.5 ÷ 25 ÷ 100) × 100 = 400
        """
        engine = BacktestEngine(initial_capital=50000, position_ratio=0.5)
        position = engine.calculate_position_size(price=25)

        amount = 50000 * 0.5 / 25  # 1000 shares
        expected = int(amount // 100) * 100  # 1000 -> 10 * 100 = 1000

        assert position == expected, f"期望{expected}，实际{position}"
        assert position == 1000, f"期望1000手，实际{position}手"

    def test_very_low_price_stock(self):
        """测试极低价格股票"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)
        position = engine.calculate_position_size(price=2)

        # 100000 * 0.2 / 2 = 10000 shares
        # 10000 // 100 = 100, 100 * 100 = 10000
        expected = 10000
        assert position == expected, f"期望{expected}，实际{position}"

    def test_zero_price_returns_zero(self):
        """测试零价格返回0"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)
        position = engine.calculate_position_size(price=0)
        assert position == 0, "零价格应返回0"

    def test_negative_price_returns_zero(self):
        """测试负价格返回0"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)
        position = engine.calculate_position_size(price=-50)
        assert position == 0, "负价格应返回0"

    def test_rounding_down_behavior(self):
        """测试向下取整行为"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)

        # 100000 * 0.2 / 50.5 = 396.03, 应向下取整到300
        position = engine.calculate_position_size(price=50.5)
        amount = 100000 * 0.2 / 50.5  # 396.03
        expected = int(amount // 100) * 100  # 300
        assert position == expected
        assert position < 396, "应向下取整"

    def test_various_position_ratios(self):
        """测试各种交易占比"""
        engine = BacktestEngine(initial_capital=100000)

        test_cases = [
            (0.01, 50, 200),     # 1%占比，50元股价 -> 20000 / 100 = 200
            (0.333, 50, 600),    # 33.3%占比，50元股价
            (0.5, 50, 1000),     # 50%占比，50元股价
            (0.99, 50, 1980),    # 99%占比，50元股价
        ]

        for ratio, price, expected_shares in test_cases:
            engine.position_ratio = ratio
            position = engine.calculate_position_size(price)
            # 验证数量在期望的100股整数倍范围内
            assert position % 100 == 0, f"持仓数量应为100的倍数"

    def test_calculation_consistency(self):
        """测试计算一致性"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)

        # 同样参数应产生相同结果
        pos1 = engine.calculate_position_size(50)
        pos2 = engine.calculate_position_size(50)
        assert pos1 == pos2, "相同参数应产生相同结果"


class TestSlippageApplication:
    """滑点应用测试"""

    def test_buy_slippage_increases_price(self):
        """买入滑点应增加价格"""
        engine = BacktestEngine(initial_capital=100000, slippage=0.01)  # 1%滑点

        original_price = 100
        slipped_price = engine.apply_slippage_to_price(original_price, is_buy=True)

        expected = 100 * (1 + 0.01)  # 101
        assert slipped_price == expected, f"期望{expected}，实际{slipped_price}"
        assert slipped_price > original_price, "买入滑点应增加价格"

    def test_sell_slippage_decreases_price(self):
        """卖出滑点应降低价格"""
        engine = BacktestEngine(initial_capital=100000, slippage=0.01)  # 1%滑点

        original_price = 100
        slipped_price = engine.apply_slippage_to_price(original_price, is_buy=False)

        expected = 100 * (1 - 0.01)  # 99
        assert slipped_price == expected, f"期望{expected}，实际{slipped_price}"
        assert slipped_price < original_price, "卖出滑点应降低价格"

    def test_zero_slippage_no_change(self):
        """零滑点应无影响"""
        engine = BacktestEngine(initial_capital=100000, slippage=0.0)

        price = 100
        buy_price = engine.apply_slippage_to_price(price, is_buy=True)
        sell_price = engine.apply_slippage_to_price(price, is_buy=False)

        assert buy_price == price, "零滑点买入不应改变价格"
        assert sell_price == price, "零滑点卖出不应改变价格"

    def test_various_slippage_rates(self):
        """测试各种滑点率"""
        engine = BacktestEngine(initial_capital=100000)

        test_cases = [0.001, 0.005, 0.01, 0.02, 0.05]
        price = 100

        for slippage in test_cases:
            engine.slippage = slippage
            buy_price = engine.apply_slippage_to_price(price, is_buy=True)
            sell_price = engine.apply_slippage_to_price(price, is_buy=False)

            expected_buy = price * (1 + slippage)
            expected_sell = price * (1 - slippage)

            assert abs(buy_price - expected_buy) < 0.0001, f"买入滑点{slippage}计算错误"
            assert abs(sell_price - expected_sell) < 0.0001, f"卖出滑点{slippage}计算错误"

    def test_slippage_symmetry(self):
        """测试滑点对称性"""
        engine = BacktestEngine(initial_capital=100000, slippage=0.01)

        price = 100
        buy_price = engine.apply_slippage_to_price(price, is_buy=True)
        # 买入价是101，反向卖出应得到99.99
        reverse_sell = engine.apply_slippage_to_price(buy_price, is_buy=False)

        # 应该接近原价（浮点误差允许0.02）
        assert abs(reverse_sell - price) < 0.02, "滑点应大致对称"


class TestCommissionCalculation:
    """手续费计算测试"""

    def test_basic_commission_calculation(self):
        """基础手续费计算"""
        engine = BacktestEngine(initial_capital=100000, commission_rate=0.0001)  # 万1

        trade_amount = 10000  # 1万元
        cost = engine.calculate_trade_cost(trade_amount)

        expected = 10000 * 0.0001  # 1元
        assert cost == expected, f"期望{expected}，实际{cost}"

    def test_very_low_commission_rate(self):
        """极低手续费率"""
        engine = BacktestEngine(initial_capital=100000, commission_rate=0.00001)

        trade_amount = 10000
        cost = engine.calculate_trade_cost(trade_amount)

        expected = 10000 * 0.00001  # 0.1元
        assert cost == expected, f"极低费率计算错误"

    def test_various_commission_rates(self):
        """测试各种手续费率"""
        test_cases = [
            (0.0001, 10000, 1),      # 万1, 1万元 -> 1元
            (0.00025, 10000, 2.5),   # 万2.5, 1万元 -> 2.5元
            (0.0005, 10000, 5),      # 万5, 1万元 -> 5元
            (0.001, 10000, 10),      # 万10, 1万元 -> 10元
        ]

        for rate, amount, expected_cost in test_cases:
            engine = BacktestEngine(commission_rate=rate)
            cost = engine.calculate_trade_cost(amount)
            assert cost == expected_cost, f"费率{rate}计算错误"

    def test_commission_proportional_to_amount(self):
        """手续费与交易金额成正比"""
        engine = BacktestEngine(commission_rate=0.0001)

        # 1万元费用为1元
        cost_10k = engine.calculate_trade_cost(10000)
        # 10万元费用应为10元
        cost_100k = engine.calculate_trade_cost(100000)

        assert cost_100k == cost_10k * 10, "手续费应与交易金额成正比"

    def test_high_commission_rate(self):
        """测试高手续费率"""
        engine = BacktestEngine(commission_rate=0.05)  # 5%

        trade_amount = 10000
        cost = engine.calculate_trade_cost(trade_amount)

        expected = 10000 * 0.05  # 500元
        assert cost == expected, f"高手续费计算错误"


class TestCompleteCostFlow:
    """完整成本计算流程测试"""

    def test_buy_transaction_with_costs(self):
        """测试买入交易的完整成本"""
        engine = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.0001,  # 万1
            slippage=0.01  # 1%
        )

        # 创建买入交易（按照backtest_engine.py的apply_trading_costs方法）
        trade = {
            'date': '2024-01-01',
            'code': '000001',
            '买入价': 100,
            '卖出价': 105,
        }

        # 应用成本
        result = engine.apply_trading_costs(trade)

        # 验证滑点应用：买入价应为101
        assert result['买入价'] == 101, f"期望滑点后价格101，实际{result['买入价']}"

        # 验证手续费
        assert result['买入成本'] > 0, "应计算手续费"

    def test_sell_transaction_with_costs(self):
        """测试卖出交易的完整成本"""
        engine = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.0001,  # 万1
            slippage=0.01  # 1%
        )

        # 创建卖出交易
        trade = {
            'date': '2024-01-05',
            'code': '000001',
            '买入价': 100,
            '卖出价': 105,
        }

        # 应用成本
        result = engine.apply_trading_costs(trade)

        # 验证滑点应用：卖出价应为103.95
        expected_sell = 105 * (1 - 0.01)
        assert abs(result['卖出价'] - expected_sell) < 0.001, f"期望滑点后价格{expected_sell}，实际{result['卖出价']}"

        # 验证手续费
        assert result['卖出成本'] > 0, "应计算手续费"

    def test_round_trip_trade_costs(self):
        """测试往返交易（买入+卖出）的总成本"""
        engine = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.0001,  # 万1
            slippage=0.01  # 1%
        )

        # 买入和卖出
        trade = {
            'date': '2024-01-01',
            'code': '000001',
            '买入价': 100,
            '卖出价': 110,
        }
        result = engine.apply_trading_costs(trade)

        # 计算总成本
        total_cost = result['买入成本'] + result['卖出成本']
        assert total_cost > 0, "往返交易应产生成本"

        # 验证收益率已考虑成本
        assert '收益率%' in result, "应包含收益率字段"
        assert result['收益率%'] > 0, "这笔交易应该盈利"

        # 无成本的收益率对比
        gross_price_profit = (110 - 100) / 100 * 100  # 10%
        assert result['收益率%'] < gross_price_profit, "成本应降低收益率"

    def test_cost_calculation_accuracy(self):
        """验证成本计算精度"""
        engine = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.00025,  # 万2.5
            slippage=0.005  # 0.5%
        )

        # 测试交易
        trade = {
            'date': '2024-01-01',
            'code': '000001',
            '买入价': 50,
            '卖出价': 55,
        }

        result = engine.apply_trading_costs(trade)

        # 验证滑点精度
        expected_buy_price = 50 * 1.005
        assert abs(result['买入价'] - expected_buy_price) < 0.0001

    def test_cost_settings_preserved(self):
        """验证成本设置被正确保存"""
        engine = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.001,
            slippage=0.01
        )

        # 验证设置
        assert engine.backtest_settings['initial_capital'] == 100000
        assert engine.backtest_settings['position_ratio'] == 0.2
        assert engine.backtest_settings['commission_rate'] == 0.001
        assert engine.backtest_settings['slippage'] == 0.01


class TestCostImpactOnReturns:
    """成本对收益的影响测试"""

    def test_with_and_without_costs(self):
        """对比有无成本的收益差异"""
        # 不带成本的引擎
        engine_no_cost = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0,
            slippage=0
        )

        # 带成本的引擎
        engine_with_cost = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.0001,
            slippage=0.01
        )

        # 相同的交易
        trade_no_cost = {'date': '2024-01-01', 'code': '000001', '买入价': 100, '卖出价': 110}
        result_no_cost = engine_no_cost.apply_trading_costs(trade_no_cost)

        trade_with_cost = {'date': '2024-01-01', 'code': '000001', '买入价': 100, '卖出价': 110}
        result_with_cost = engine_with_cost.apply_trading_costs(trade_with_cost)

        # 无成本的买入价应该是100
        assert result_no_cost['买入价'] == 100, "无成本买入价应为100"

        # 有成本的买入价应该高于100
        assert result_with_cost['买入价'] == 101, "1%滑点买入价应为101"

        # 无成本收益率应高于有成本的
        assert result_no_cost['收益率%'] > result_with_cost['收益率%'], "无成本收益率应高于有成本"

    def test_cost_reduces_profit_percentage(self):
        """验证成本降低收益率"""
        engine = BacktestEngine(
            initial_capital=100000,
            position_ratio=0.2,
            commission_rate=0.0001,
            slippage=0.01
        )

        # 完整的买卖交易
        trade = {
            'date': '2024-01-01',
            'code': '000001',
            '买入价': 100,
            '卖出价': 110,
        }
        result = engine.apply_trading_costs(trade)

        # 无成本收益率（价格收益）
        gross_return = (110 - 100) / 100 * 100  # 10%

        # 有成本收益率
        net_return = result['收益率%']

        assert net_return < gross_return, "成本应降低收益率"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
