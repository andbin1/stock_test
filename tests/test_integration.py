"""集成测试 - 测试完整的回测流程"""
import pytest
import pandas as pd
from unittest.mock import patch
from backtest_engine import BacktestEngine
from strategy import VolumeBreakoutStrategy, SteadyTrendStrategy
from data_manager import DataManager
from indicators import add_all_indicators


@pytest.mark.integration
class TestEndToEndBacktest:
    """端到端回测流程测试"""

    def test_complete_backtest_workflow(self, sample_stock_data, sample_strategy_params):
        """测试完整的回测流程"""
        # 1. 准备数据
        df = sample_stock_data.copy()

        # 2. 创建策略
        strategy = VolumeBreakoutStrategy(sample_strategy_params)

        # 3. 创建回测引擎
        engine = BacktestEngine(initial_capital=100000, commission_rate=0.0005)

        # 4. 运行回测
        result = engine.run_single_stock("000001", df, strategy)

        # 5. 验证结果
        assert 'symbol' in result
        assert 'num_trades' in result
        assert 'total_return' in result
        assert 'win_rate' in result

    def test_multiple_stocks_backtest_workflow(self, sample_multiple_stocks_data, sample_strategy_params):
        """测试多股票回测流程"""
        # 1. 准备数据
        stocks_data = sample_multiple_stocks_data

        # 2. 创建策略
        strategy = VolumeBreakoutStrategy(sample_strategy_params)

        # 3. 创建回测引擎
        engine = BacktestEngine()

        # 4. 运行多股票回测
        results = engine.run_multiple_stocks(stocks_data, strategy)

        # 5. 聚合结果
        agg_result = engine.aggregate_results(results)

        # 6. 验证聚合结果
        assert 'stocks_count' in agg_result
        assert 'total_trades' in agg_result
        assert 'avg_return_per_trade' in agg_result

    def test_strategy_with_indicators(self, sample_stock_data, sample_strategy_params):
        """测试策略与指标计算的集成"""
        # 1. 添加指标
        df_with_indicators = add_all_indicators(sample_stock_data)

        # 2. 创建策略
        strategy = VolumeBreakoutStrategy(sample_strategy_params)

        # 3. 计算信号
        df_signals = strategy.calculate_signals(df_with_indicators)

        # 4. 验证信号列和指标列都存在
        assert 'Buy_Signal' in df_signals.columns
        assert 'Sell_Signal' in df_signals.columns
        assert 'MA5' in df_signals.columns
        assert 'MA30' in df_signals.columns


@pytest.mark.integration
class TestDataFlowIntegration:
    """测试数据流转集成"""

    @patch('data_manager.get_stock_data')
    def test_data_fetch_cache_backtest_flow(self, mock_get_stock_data, tmp_path, monkeypatch, sample_stock_data, sample_strategy_params):
        """测试数据获取->缓存->回测的完整流程"""
        # Mock数据获取
        mock_get_stock_data.return_value = sample_stock_data.copy()

        # 创建临时数据管理器
        import data_manager
        test_dir = tmp_path / "data_cache"
        test_dir.mkdir()
        monkeypatch.setattr(data_manager, 'DATA_DIR', test_dir)
        monkeypatch.setattr(data_manager, 'DB_FILE', test_dir / "test_db.db")
        monkeypatch.setattr(data_manager, 'CACHE_DIR', test_dir / "cache")

        # 1. 获取并缓存数据
        manager = DataManager()
        df = manager.fetch_and_cache("000001", "20240101", "20241231")

        assert df is not None

        # 2. 从缓存读取数据
        df_cached = manager.get_data_from_cache("000001", "20240101", "20241231")

        assert df_cached is not None
        assert len(df_cached) > 0

        # 3. 运行回测
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        result = engine.run_single_stock("000001", df_cached, strategy)

        # 4. 验证回测结果
        assert result['symbol'] == "000001"


@pytest.mark.integration
class TestMultiStrategyComparison:
    """测试多策略对比"""

    def test_compare_strategies(self, sample_stock_data, sample_strategy_params, sample_steady_trend_params):
        """测试不同策略的对比"""
        df = sample_stock_data

        # 策略1：量能突破
        strategy1 = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        result1 = engine.run_single_stock("000001", df, strategy1)

        # 策略2：稳健趋势
        strategy2 = SteadyTrendStrategy(sample_steady_trend_params)
        result2 = engine.run_single_stock("000001", df, strategy2)

        # 验证两个策略都能正常运行
        assert 'total_return' in result1
        assert 'total_return' in result2

        # 两个策略的结果应该不同（除非恰好相同）
        # 至少验证结构正确
        assert isinstance(result1['num_trades'], int)
        assert isinstance(result2['num_trades'], int)


@pytest.mark.integration
class TestPerformanceUnderDifferentMarketConditions:
    """测试不同市场条件下的表现"""

    def test_bull_market_performance(self, sample_strategy_params):
        """测试牛市表现"""
        # 创建上涨趋势数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        dates = dates[dates.dayofweek < 5]
        n = len(dates)

        df_bull = pd.DataFrame({
            '日期': dates,
            '开盘': pd.Series(range(10, 10 + n)) * 0.99,
            '收盘': pd.Series(range(10, 10 + n)),  # 持续上涨
            '高': pd.Series(range(10, 10 + n)) * 1.02,
            '低': pd.Series(range(10, 10 + n)) * 0.98,
            '成交量': [5000000] * n,
            '成交额': [50000000] * n,
            '振幅': [2.0] * n,
            '涨跌幅': [1.0] * n,
            '涨跌': [0.1] * n,
            '换手率': [2.0] * n,
        })

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        result = engine.run_single_stock("TEST_BULL", df_bull, strategy)

        # 牛市中应该有交易
        assert result is not None

    def test_bear_market_performance(self, sample_strategy_params):
        """测试熊市表现"""
        # 创建下跌趋势数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        dates = dates[dates.dayofweek < 5]
        n = len(dates)

        df_bear = pd.DataFrame({
            '日期': dates,
            '开盘': pd.Series(range(20, 20 - n, -1)) * 0.99,
            '收盘': pd.Series(range(20, 20 - n, -1)),  # 持续下跌
            '高': pd.Series(range(20, 20 - n, -1)) * 1.02,
            '低': pd.Series(range(20, 20 - n, -1)) * 0.98,
            '成交量': [5000000] * n,
            '成交额': [50000000] * n,
            '振幅': [2.0] * n,
            '涨跌幅': [-1.0] * n,
            '涨跌': [-0.1] * n,
            '换手率': [2.0] * n,
        })

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        result = engine.run_single_stock("TEST_BEAR", df_bear, strategy)

        # 验证能正常运行
        assert result is not None

    def test_sideways_market_performance(self, sample_strategy_params):
        """测试震荡市表现"""
        # 创建震荡数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        dates = dates[dates.dayofweek < 5]
        n = len(dates)

        import numpy as np
        # 使用正弦波创建震荡
        prices = 15 + 5 * np.sin(np.linspace(0, 4 * np.pi, n))

        df_sideways = pd.DataFrame({
            '日期': dates,
            '开盘': prices * 0.99,
            '收盘': prices,
            '高': prices * 1.02,
            '低': prices * 0.98,
            '成交量': [5000000] * n,
            '成交额': [50000000] * n,
            '振幅': [2.0] * n,
            '涨跌幅': [0.5] * n,
            '涨跌': [0.05] * n,
            '换手率': [2.0] * n,
        })

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        result = engine.run_single_stock("TEST_SIDEWAYS", df_sideways, strategy)

        assert result is not None


@pytest.mark.integration
class TestErrorPropagation:
    """测试错误传播和恢复"""

    def test_partial_data_corruption(self, sample_stock_data, sample_strategy_params):
        """测试部分数据损坏"""
        df = sample_stock_data.copy()

        # 故意制造一些NaN值
        df.loc[10:15, '收盘'] = None

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()

        # 应该能处理部分缺失数据
        result = engine.run_single_stock("000001", df, strategy)

        # 应该返回结果，而不是抛出异常
        assert result is not None

    @patch('data_manager.get_stock_data')
    def test_network_failure_recovery(self, mock_get_stock_data, tmp_path, monkeypatch, sample_stock_data):
        """测试网络失败后的恢复"""
        # 第一次失败，第二次成功
        mock_get_stock_data.side_effect = [None, sample_stock_data.copy()]

        import data_manager
        test_dir = tmp_path / "data_cache"
        test_dir.mkdir()
        monkeypatch.setattr(data_manager, 'DATA_DIR', test_dir)
        monkeypatch.setattr(data_manager, 'DB_FILE', test_dir / "test_db.db")
        monkeypatch.setattr(data_manager, 'CACHE_DIR', test_dir / "cache")

        manager = DataManager()

        # 第一次获取失败
        df1 = manager.fetch_and_cache("000001", "20240101", "20241231")
        assert df1 is None

        # 第二次获取成功
        df2 = manager.fetch_and_cache("000001", "20240101", "20241231", force_refresh=True)
        assert df2 is not None


@pytest.mark.integration
class TestScalability:
    """测试可扩展性"""

    @patch('data_manager.get_stock_data')
    def test_batch_processing_many_stocks(self, mock_get_stock_data, tmp_path, monkeypatch, sample_stock_data, sample_strategy_params):
        """测试批量处理多只股票"""
        mock_get_stock_data.return_value = sample_stock_data.copy()

        import data_manager
        test_dir = tmp_path / "data_cache"
        test_dir.mkdir()
        monkeypatch.setattr(data_manager, 'DATA_DIR', test_dir)
        monkeypatch.setattr(data_manager, 'DB_FILE', test_dir / "test_db.db")
        monkeypatch.setattr(data_manager, 'CACHE_DIR', test_dir / "cache")

        manager = DataManager()

        # 批量获取10只股票
        symbols = [f"00000{i}" for i in range(1, 11)]
        stocks_data = manager.batch_fetch_and_cache(symbols, "20240101", "20241231")

        # 运行回测
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        results = engine.run_multiple_stocks(stocks_data, strategy)

        # 聚合结果
        agg_result = engine.aggregate_results(results)

        # 验证能处理多只股票
        assert isinstance(agg_result, dict)
        assert 'stocks_count' in agg_result


@pytest.mark.integration
@pytest.mark.slow
class TestLongRunningBacktest:
    """测试长期回测"""

    def test_multi_year_backtest(self, sample_strategy_params):
        """测试多年回测"""
        # 创建2年的数据
        dates = pd.date_range('2022-01-01', '2024-01-01', freq='D')
        dates = dates[dates.dayofweek < 5]
        n = len(dates)

        import numpy as np
        close_prices = 10 + np.cumsum(np.random.randn(n) * 0.1)
        close_prices = np.maximum(close_prices, 1)  # 确保为正

        df = pd.DataFrame({
            '日期': dates,
            '开盘': close_prices * 0.99,
            '收盘': close_prices,
            '高': close_prices * 1.02,
            '低': close_prices * 0.98,
            '成交量': np.random.randint(1000000, 10000000, n),
            '成交额': np.random.randint(10000000, 100000000, n),
            '振幅': np.random.uniform(1, 5, n),
            '涨跌幅': np.random.uniform(-3, 3, n),
            '涨跌': np.random.uniform(-0.5, 0.5, n),
            '换手率': np.random.uniform(0.5, 5, n),
        })

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        engine = BacktestEngine()
        result = engine.run_single_stock("LONG_TEST", df, strategy)

        # 验证能处理长期数据
        assert result is not None
        assert 'num_trades' in result
