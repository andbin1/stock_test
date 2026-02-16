"""测试backtest_engine.py - 回测引擎模块"""
import pytest
import pandas as pd
import numpy as np
from backtest_engine import BacktestEngine


class MockStrategy:
    """模拟策略类用于测试"""

    def __init__(self, trades=None):
        self.trades = trades or []

    def get_trades(self, df):
        return self.trades


class TestBacktestEngine:
    """测试BacktestEngine基本功能"""

    def test_init_default_params(self):
        """测试默认参数初始化"""
        engine = BacktestEngine()
        assert engine.initial_capital == 100000
        assert engine.commission_rate == 0.0005

    def test_init_custom_params(self):
        """测试自定义参数初始化"""
        engine = BacktestEngine(initial_capital=200000, commission_rate=0.001)
        assert engine.initial_capital == 200000
        assert engine.commission_rate == 0.001


class TestRunSingleStock:
    """测试单只股票回测"""

    def test_run_single_stock_no_trades(self, sample_stock_data):
        """测试无交易情况"""
        engine = BacktestEngine()
        strategy = MockStrategy(trades=[])

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['symbol'] == "000001"
        assert result['trades'] == []
        assert result['total_return'] == 0
        assert result['num_trades'] == 0
        assert result['win_rate'] == 0
        assert result['avg_return'] == 0
        assert result['max_loss'] == 0
        assert result['profit_factor'] == 0

    def test_run_single_stock_with_trades(self, sample_stock_data, sample_trades):
        """测试有交易的情况"""
        engine = BacktestEngine()
        strategy = MockStrategy(trades=sample_trades)

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['symbol'] == "000001"
        assert result['num_trades'] == 3
        assert len(result['trades']) == 3
        assert 'trades_df' in result

        # 验证总收益
        trades_df = pd.DataFrame(sample_trades)
        expected_return = trades_df['收益率%'].sum()
        assert result['total_return'] == pytest.approx(expected_return, rel=1e-5)

    def test_run_single_stock_win_rate_calculation(self, sample_stock_data):
        """测试胜率计算"""
        trades = [
            {'收益率%': 10.0},  # 赢
            {'收益率%': -5.0},  # 输
            {'收益率%': 8.0},   # 赢
            {'收益率%': 0.0},   # 输（收益为0算输）
        ]
        engine = BacktestEngine()
        strategy = MockStrategy(trades=trades)

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['num_trades'] == 4
        assert result['win_rate'] == 50.0  # 2赢2输

    def test_run_single_stock_profit_factor(self, sample_stock_data):
        """测试盈亏比计算"""
        trades = [
            {'收益率%': 10.0},  # 赢
            {'收益率%': 20.0},  # 赢
            {'收益率%': -5.0},  # 输
            {'收益率%': -10.0}, # 输
        ]
        engine = BacktestEngine()
        strategy = MockStrategy(trades=trades)

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        # 平均盈利 = (10 + 20) / 2 = 15
        # 平均亏损 = (5 + 10) / 2 = 7.5
        # 盈亏比 = 15 / 7.5 = 2.0
        assert result['profit_factor'] == pytest.approx(2.0, rel=1e-5)

    def test_run_single_stock_max_loss(self, sample_stock_data):
        """测试最大单笔亏损"""
        trades = [
            {'收益率%': 10.0},
            {'收益率%': -15.0},  # 最大亏损
            {'收益率%': -5.0},
        ]
        engine = BacktestEngine()
        strategy = MockStrategy(trades=trades)

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['max_loss'] == -15.0

    def test_run_single_stock_all_wins(self, sample_stock_data):
        """测试全部盈利的情况"""
        trades = [
            {'收益率%': 10.0},
            {'收益率%': 5.0},
            {'收益率%': 8.0},
        ]
        engine = BacktestEngine()
        strategy = MockStrategy(trades=trades)

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['win_rate'] == 100.0
        # 盈亏比应该是1（因为没有亏损，avg_loss=0）
        assert result['profit_factor'] == 1.0

    def test_run_single_stock_all_losses(self, sample_stock_data):
        """测试全部亏损的情况"""
        trades = [
            {'收益率%': -5.0},
            {'收益率%': -8.0},
            {'收益率%': -3.0},
        ]
        engine = BacktestEngine()
        strategy = MockStrategy(trades=trades)

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['win_rate'] == 0.0
        # 盈亏比应该是0（没有盈利）
        assert result['profit_factor'] == 0.0


class TestRunMultipleStocks:
    """测试多只股票回测"""

    def test_run_multiple_stocks_basic(self, sample_multiple_stocks_data):
        """测试基本的多股票回测"""
        trades = [{'收益率%': 10.0}]
        strategy = MockStrategy(trades=trades)
        engine = BacktestEngine()

        results = engine.run_multiple_stocks(sample_multiple_stocks_data, strategy)

        assert len(results) == 3
        assert '000001' in results
        assert '000002' in results
        assert '600000' in results

    def test_run_multiple_stocks_skip_insufficient_data(self, sample_stock_data_short):
        """测试跳过数据不足的股票"""
        stocks_data = {
            '000001': sample_stock_data_short,  # 数据不足
            '000002': None,  # 无数据
        }
        trades = [{'收益率%': 10.0}]
        strategy = MockStrategy(trades=trades)
        engine = BacktestEngine()

        results = engine.run_multiple_stocks(stocks_data, strategy)

        # 数据不足的股票应该被跳过
        assert len(results) == 0

    def test_run_multiple_stocks_skip_no_trades(self, sample_multiple_stocks_data):
        """测试跳过无交易的股票"""
        strategy = MockStrategy(trades=[])  # 无交易
        engine = BacktestEngine()

        results = engine.run_multiple_stocks(sample_multiple_stocks_data, strategy)

        # 无交易的股票应该被跳过
        assert len(results) == 0


class TestAggregateResults:
    """测试结果聚合"""

    def test_aggregate_results_empty(self):
        """测试空结果聚合"""
        engine = BacktestEngine()
        result = engine.aggregate_results({})

        assert result['total_trades'] == 0
        assert result['total_return'] == 0
        assert result['stocks_count'] == 0
        assert result['avg_return_per_trade'] == 0
        assert result['win_rate'] == 0

    def test_aggregate_results_basic(self):
        """测试基本的结果聚合"""
        trades_df1 = pd.DataFrame([
            {'收益率%': 10.0},
            {'收益率%': -5.0},
        ])
        trades_df2 = pd.DataFrame([
            {'收益率%': 8.0},
            {'收益率%': 12.0},
        ])

        results = {
            '000001': {
                'trades_df': trades_df1,
                'num_trades': 2,
            },
            '000002': {
                'trades_df': trades_df2,
                'num_trades': 2,
            },
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        assert agg_result['stocks_count'] == 2
        assert agg_result['total_trades'] == 4
        assert agg_result['total_return'] == pytest.approx(25.0, rel=1e-5)
        assert agg_result['avg_return_per_trade'] == pytest.approx(6.25, rel=1e-5)

    def test_aggregate_results_win_rate(self):
        """测试聚合结果的胜率计算"""
        trades_df1 = pd.DataFrame([
            {'收益率%': 10.0},  # 赢
            {'收益率%': -5.0},  # 输
        ])
        trades_df2 = pd.DataFrame([
            {'收益率%': 8.0},   # 赢
            {'收益率%': -3.0},  # 输
        ])

        results = {
            '000001': {'trades_df': trades_df1, 'num_trades': 2},
            '000002': {'trades_df': trades_df2, 'num_trades': 2},
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        # 2赢2输，胜率50%
        assert agg_result['win_rate'] == pytest.approx(50.0, rel=1e-5)

    def test_aggregate_results_profit_factor(self):
        """测试聚合结果的盈亏比"""
        trades_df = pd.DataFrame([
            {'收益率%': 10.0},  # 赢
            {'收益率%': 20.0},  # 赢
            {'收益率%': -5.0},  # 输
            {'收益率%': -10.0}, # 输
        ])

        results = {
            '000001': {'trades_df': trades_df, 'num_trades': 4},
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        # 平均盈利 = 15, 平均亏损 = 7.5, 盈亏比 = 2.0
        assert agg_result['avg_profit'] == pytest.approx(15.0, rel=1e-5)
        assert agg_result['avg_loss'] == pytest.approx(7.5, rel=1e-5)
        assert agg_result['profit_factor'] == pytest.approx(2.0, rel=1e-5)

    def test_aggregate_results_max_min_return(self):
        """测试聚合结果的最大最小收益"""
        trades_df = pd.DataFrame([
            {'收益率%': 10.0},
            {'收益率%': -15.0},  # 最小
            {'收益率%': 25.0},   # 最大
        ])

        results = {
            '000001': {'trades_df': trades_df, 'num_trades': 3},
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        assert agg_result['max_single_return'] == 25.0
        assert agg_result['min_single_return'] == -15.0

    def test_aggregate_results_no_trades_df(self):
        """测试没有trades_df的结果"""
        results = {
            '000001': {'num_trades': 2},  # 没有trades_df
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        # 应该返回默认值
        assert agg_result['total_trades'] == 0
        assert agg_result['stocks_count'] == 0


class TestEdgeCases:
    """测试边界情况"""

    def test_divide_by_zero_protection(self):
        """测试除零保护"""
        # 只有亏损，没有盈利的情况
        trades_df = pd.DataFrame([
            {'收益率%': -5.0},
            {'收益率%': -10.0},
        ])

        results = {
            '000001': {'trades_df': trades_df, 'num_trades': 2},
        }

        engine = BacktestEngine()
        agg_result = engine.aggregate_results(results)

        # 盈亏比应该是0（没有盈利）
        assert agg_result['profit_factor'] == 0.0

    def test_single_trade_statistics(self, sample_stock_data):
        """测试单笔交易的统计"""
        trades = [{'收益率%': 10.0}]
        strategy = MockStrategy(trades=trades)
        engine = BacktestEngine()

        result = engine.run_single_stock("000001", sample_stock_data, strategy)

        assert result['num_trades'] == 1
        assert result['win_rate'] == 100.0
        assert result['total_return'] == 10.0
