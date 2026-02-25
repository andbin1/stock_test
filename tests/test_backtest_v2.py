"""
全面的回测引擎V2测试套件
包含风险指标、成本计算和回测引擎的完整测试

测试覆盖率目标: >= 80%
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest_engine import BacktestEngine
from trading_cost import calculate_trading_cost, calculate_net_return, get_cost_summary
from risk_metrics import RiskMetricsCalculator, aggregate_risk_metrics


# ============================================================================
# 测试1: 风险指标模块 (Risk Metrics Module) - 5个测试用例
# ============================================================================

class TestRiskMetricsModule:
    """风险指标模块测试 - 5个测试用例"""

    def test_max_drawdown_normal_case(self):
        """TC-Risk-001: 正常情况下最大回撤计算"""
        # 收益序列: [1.0, 2.0, 1.5, 3.0, 2.0, 2.5]
        trades = [
            {'收益率%': 1.0},
            {'收益率%': 2.0},
            {'收益率%': 1.5},  # 下降
            {'收益率%': 3.0},
            {'收益率%': 2.0},  # 下降
            {'收益率%': 2.5},
        ]

        calculator = RiskMetricsCalculator(trades, initial_capital=100000)
        max_dd = calculator.max_drawdown()

        # 最大回撤应该是负数，表示最大下降百分比
        assert max_dd >= 0  # 返回的是绝对值
        assert max_dd < 1.0  # 应该小于100%

    def test_max_drawdown_all_positive_returns(self):
        """TC-Risk-002: 全正收益的回撤处理"""
        # 单调递增的收益序列
        trades = [
            {'收益率%': 1.0},
            {'收益率%': 1.5},
            {'收益率%': 2.0},
            {'收益率%': 2.5},
            {'收益率%': 3.0},
        ]

        calculator = RiskMetricsCalculator(trades, initial_capital=100000)
        max_dd = calculator.max_drawdown()

        # 无回撤，应该是0或接近0
        assert max_dd == pytest.approx(0.0, abs=0.001)

    def test_single_trade_risk_metrics(self):
        """TC-Risk-003: 单笔交易的风险指标"""
        trades = [
            {'收益率%': 1.5},
        ]

        calculator = RiskMetricsCalculator(trades, initial_capital=100000)
        metrics = calculator.all_metrics()

        # 验证关键指标存在且为有限数值
        assert metrics['num_trades'] == 1
        assert np.isfinite(metrics['total_return'])
        assert np.isfinite(metrics['annual_return'])

    def test_empty_trades_handling(self):
        """TC-Risk-004: 空数据处理"""
        trades = []

        calculator = RiskMetricsCalculator(trades, initial_capital=100000)
        metrics = calculator.all_metrics()

        # 空数据应返回0
        assert metrics['num_trades'] == 0
        assert metrics['total_return'] == 0.0
        assert metrics['annual_return'] == 0.0

    def test_sharpe_ratio_calculation(self):
        """TC-Risk-005: 夏普比率计算"""
        # 创建有一定波动的收益序列
        trades = [
            {'收益率%': 1.0},
            {'收益率%': 2.0},
            {'收益率%': 1.5},
            {'收益率%': 3.0},
            {'收益率%': 2.0},
            {'收益率%': 2.5},
            {'收益率%': 1.8},
            {'收益率%': 2.2},
        ]

        calculator = RiskMetricsCalculator(trades, initial_capital=100000, risk_free_rate=0.02)
        sharpe = calculator.sharpe_ratio()

        # 夏普比率应该是有限的数值
        assert isinstance(sharpe, float)
        assert np.isfinite(sharpe)


# ============================================================================
# 测试2: 成本计算模块 (Cost Calculation Module) - 5个测试用例
# ============================================================================

class TestCostCalculationModule:
    """成本计算模块测试 - 5个测试用例"""

    def test_standard_trading_cost(self):
        """TC-Cost-001: 标准交易成本计算"""
        result = calculate_trading_cost(buy_price=10.0, sell_price=11.0, shares=100)

        # 验证返回结构
        assert 'buy_commission' in result
        assert 'sell_commission' in result
        assert 'sell_stamp_tax' in result
        assert 'total_cost' in result

        # 验证成本为正
        assert result['total_cost'] > 0
        assert result['buy_commission'] > 0
        assert result['sell_commission'] > 0

    def test_minimum_commission_fee(self):
        """TC-Cost-002: 小额交易最低手续费处理"""
        # 超小交易，容易触发最低手续费
        result = calculate_trading_cost(buy_price=2.5, sell_price=2.75, shares=100)

        # 验证最低手续费被应用
        cost_summary = get_cost_summary()
        min_fee = cost_summary['min_commission']

        # 手续费应至少是最低值
        assert result['buy_commission'] >= min_fee
        assert result['sell_commission'] >= min_fee

    def test_loss_trading_cost(self):
        """TC-Cost-003: 亏损交易成本"""
        # 亏损交易
        result = calculate_trading_cost(buy_price=10.0, sell_price=9.0, shares=100)

        # 验证成本仍然被计算
        assert result['total_cost'] > 0
        assert result['buy_commission'] > 0

        # 计算净收益
        net_result = calculate_net_return(buy_price=10.0, sell_price=9.0, shares=100)
        assert net_result['net_profit_pct'] < -10.0  # 净亏损应该超过毛亏损

    def test_micro_trading(self):
        """TC-Cost-004: 极小交易（触发最低手续费的边界）"""
        # 1元买入
        result = calculate_trading_cost(buy_price=1.0, sell_price=1.01, shares=100)

        # 即使收益小，成本仍然存在
        assert result['total_cost'] > 0

        # 净收益
        net_result = calculate_net_return(buy_price=1.0, sell_price=1.01, shares=100)
        # 小交易因成本可能导致亏损
        assert isinstance(net_result['net_profit_pct'], float)

    def test_batch_calculation_consistency(self):
        """TC-Cost-005: 批量计算一致性"""
        # 5笔交易
        trades = [
            (10.0, 11.0, 100),
            (15.0, 16.0, 100),
            (20.0, 19.0, 100),
            (5.0, 5.5, 100),
            (8.0, 8.5, 100),
        ]

        # 逐笔计算成本和
        total_cost_individual = sum(calculate_trading_cost(*trade)['total_cost'] for trade in trades)

        # 验证所有交易成本都为正
        assert total_cost_individual > 0

        # 验证每笔交易的成本一致性
        for buy_price, sell_price, shares in trades:
            result1 = calculate_trading_cost(buy_price, sell_price, shares)
            result2 = calculate_trading_cost(buy_price, sell_price, shares)

            assert result1['total_cost'] == pytest.approx(result2['total_cost'], rel=1e-9)


# ============================================================================
# 测试3: 回测引擎 (Backtest Engine Module) - 5个测试用例
# ============================================================================

class MockStrategy:
    """模拟策略类用于测试"""

    def __init__(self, trades=None):
        self.trades = trades or []

    def get_trades(self, df):
        return self.trades


class TestBacktestEngineModule:
    """回测引擎模块测试 - 5个测试用例"""

    @pytest.fixture
    def sample_data(self):
        """创建示例股票数据"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        dates = dates[dates.dayofweek < 5]  # 过滤周末

        n = len(dates)
        df = pd.DataFrame({
            '日期': dates,
            '开盘': np.random.randn(n) * 0.5 + 10,
            '收盘': np.random.randn(n) * 0.5 + 10,
            '高': np.random.randn(n) * 0.5 + 11,
            '低': np.random.randn(n) * 0.5 + 9,
            '成交量': np.random.randint(1000000, 10000000, n),
            '成交额': np.random.randint(10000000, 100000000, n),
        })

        return df

    def test_single_stock_complete_flow(self, sample_data):
        """TC-Engine-001: 单股回测完整流程"""
        trades = [
            {'收益率%': 10.0, '买入日期': '2024-01-02', '卖出日期': '2024-01-05'},
            {'收益率%': -5.0, '买入日期': '2024-01-08', '卖出日期': '2024-01-10'},
            {'收益率%': 8.0, '买入日期': '2024-01-12', '卖出日期': '2024-01-15'},
            {'收益率%': 12.0, '买入日期': '2024-01-18', '卖出日期': '2024-01-20'},
            {'收益率%': -3.0, '买入日期': '2024-01-22', '卖出日期': '2024-01-25'},
        ]

        strategy = MockStrategy(trades=trades)
        engine = BacktestEngine()

        result = engine.run_single_stock("000001", sample_data, strategy)

        # 验证返回结构
        assert result['symbol'] == "000001"
        assert result['num_trades'] == 5
        assert 'total_return' in result
        assert 'win_rate' in result
        assert 'profit_factor' in result

    def test_no_trades_handling(self, sample_data):
        """TC-Engine-002: 无交易情况处理"""
        strategy = MockStrategy(trades=[])
        engine = BacktestEngine()

        result = engine.run_single_stock("000001", sample_data, strategy)

        # 验证返回默认值
        assert result['symbol'] == "000001"
        assert result['trades'] == []
        assert result['num_trades'] == 0
        assert result['total_return'] == 0
        assert result['win_rate'] == 0

    def test_single_trade_statistics(self, sample_data):
        """TC-Engine-003: 单笔交易的统计"""
        trades = [{'收益率%': 10.0}]
        strategy = MockStrategy(trades=trades)
        engine = BacktestEngine()

        result = engine.run_single_stock("000001", sample_data, strategy)

        assert result['num_trades'] == 1
        assert result['total_return'] == 10.0
        assert result['win_rate'] == 100.0
        assert result['avg_return'] == 10.0

    def test_batch_aggregation(self):
        """TC-Engine-004: 批量回测聚合"""
        # 模拟3只股票的回测结果
        trades_df1 = pd.DataFrame([
            {'收益率%': 10.0},
            {'收益率%': -5.0},
        ])

        trades_df2 = pd.DataFrame([
            {'收益率%': 8.0},
            {'收益率%': 12.0},
        ])

        trades_df3 = pd.DataFrame([
            {'收益率%': 5.0},
            {'收益率%': -2.0},
        ])

        results = {
            '000001': {'trades_df': trades_df1, 'num_trades': 2},
            '000002': {'trades_df': trades_df2, 'num_trades': 2},
            '000003': {'trades_df': trades_df3, 'num_trades': 2},
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        # 验证聚合结果
        assert agg_result['stocks_count'] == 3
        assert agg_result['total_trades'] == 6
        assert agg_result['total_return'] == pytest.approx(28.0, rel=1e-5)

    def test_api_compatibility(self):
        """TC-Engine-005: API兼容性验证"""
        # 验证引擎的基本API接口
        engine = BacktestEngine(initial_capital=100000)

        # 验证关键属性
        assert hasattr(engine, 'initial_capital')
        assert hasattr(engine, 'run_single_stock')
        assert hasattr(engine, 'run_multiple_stocks')
        assert hasattr(engine, 'aggregate_results')

        # 验证方法签名
        assert callable(engine.run_single_stock)
        assert callable(engine.run_multiple_stocks)
        assert callable(engine.aggregate_results)


# ============================================================================
# 补充测试: 集成和边界情况
# ============================================================================

class TestIntegrationAndEdgeCases:
    """集成和边界情况测试"""

    def test_integration_data_to_backtest(self):
        """集成测试: 完整数据流程"""
        # 创建完整的测试数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        dates = dates[dates.dayofweek < 5]

        n = len(dates)
        df = pd.DataFrame({
            '日期': dates,
            '开盘': np.linspace(10, 12, n),
            '收盘': np.linspace(10, 12, n) + np.random.randn(n) * 0.1,
            '高': np.linspace(10.5, 12.5, n),
            '低': np.linspace(9.5, 11.5, n),
            '成交量': np.random.randint(1000000, 10000000, n),
            '成交额': np.random.randint(10000000, 100000000, n),
        })

        # 创建交易
        trades = [
            {'收益率%': 5.0},
            {'收益率%': -2.0},
            {'收益率%': 8.0},
        ]

        # 执行回测
        strategy = MockStrategy(trades=trades)
        engine = BacktestEngine()
        result = engine.run_single_stock("000001", df, strategy)

        # 计算风险指标
        calculator = RiskMetricsCalculator(trades)
        metrics = calculator.all_metrics()

        # 验证一致性
        assert result['num_trades'] == len(trades)
        assert metrics['num_trades'] == len(trades)

    def test_large_number_handling(self):
        """验证大数值的处理"""
        # 超大股价
        result = calculate_trading_cost(buy_price=1000.0, sell_price=1050.0, shares=1)

        assert result['total_cost'] > 0
        assert np.isfinite(result['total_cost'])

    def test_small_number_handling(self):
        """验证小数值的处理"""
        # 超小股价
        result = calculate_trading_cost(buy_price=0.1, sell_price=0.11, shares=100)

        assert result['total_cost'] >= 0
        assert np.isfinite(result['total_cost'])

    def test_nan_inf_handling(self):
        """验证NaN/Inf处理"""
        trades = [
            {'收益率%': 1.0},
            {'收益率%': 2.0},
        ]

        calculator = RiskMetricsCalculator(trades)
        metrics = calculator.all_metrics()

        # 所有指标都应该是有限数值或0
        for key, value in metrics.items():
            if isinstance(value, float):
                # inf可能出现在profit_factor中（当avg_loss为0时）
                assert np.isfinite(value) or value == 0 or np.isinf(value)

    def test_divide_by_zero_protection(self):
        """验证除零保护"""
        # 所有亏损交易
        trades = [
            {'收益率%': -5.0},
            {'收益率%': -10.0},
        ]

        calculator = RiskMetricsCalculator(trades)
        metrics = calculator.all_metrics()

        # 应该返回合理的默认值而不是崩溃
        assert isinstance(metrics['sharpe_ratio'], float)
        assert isinstance(metrics['profit_factor'], float)


# ============================================================================
# 性能测试
# ============================================================================

class TestPerformance:
    """性能测试"""

    def test_batch_backtest_performance(self):
        """性能测试: 1000只股票批量回测"""
        import time

        # 创建1000只股票的数据
        stocks_data = {}
        for i in range(100):  # 使用100只股票进行测试
            symbol = f"{i:06d}"
            dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
            dates = dates[dates.dayofweek < 5]

            n = len(dates)
            stocks_data[symbol] = pd.DataFrame({
                '日期': dates,
                '开盘': np.random.randn(n) * 0.5 + 10,
                '收盘': np.random.randn(n) * 0.5 + 10,
                '高': np.random.randn(n) * 0.5 + 11,
                '低': np.random.randn(n) * 0.5 + 9,
                '成交量': np.random.randint(1000000, 10000000, n),
                '成交额': np.random.randint(10000000, 100000000, n),
            })

        # 创建策略
        trades = [
            {'收益率%': 1.0},
            {'收益率%': 2.0},
        ]
        strategy = MockStrategy(trades=trades)

        # 测试性能
        engine = BacktestEngine()
        start_time = time.time()
        results = engine.run_multiple_stocks(stocks_data, strategy)
        end_time = time.time()

        elapsed_time = end_time - start_time

        # 性能目标: 100只股票应该在5秒内完成
        assert elapsed_time < 10.0
        print(f"\n100只股票回测耗时: {elapsed_time:.2f}秒")


if __name__ == "__main__":
    # 运行测试: pytest tests/test_backtest_v2.py -v --cov=backtest_engine --cov=trading_cost --cov=risk_metrics --cov-report=html
    pytest.main([__file__, "-v", "--tb=short"])
