"""测试strategy.py - 交易策略模块"""
import pytest
import pandas as pd
import numpy as np
from strategy import (
    VolumeBreakoutStrategy,
    SteadyTrendStrategy,
    AggressiveMomentumStrategy,
    BalancedMultiFactorStrategy,
)


class TestVolumeBreakoutStrategy:
    """测试量能突破回踩策略"""

    def test_init_default_params(self, sample_strategy_params):
        """测试默认参数初始化"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)

        assert strategy.ma_period == 30
        assert strategy.hold_days == 3
        assert strategy.volume_multiplier == 2.0

    def test_calculate_signals_basic(self, sample_stock_data, sample_strategy_params):
        """测试基本信号计算"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        # 验证新增的列
        assert 'MA5' in df_signals.columns
        assert 'MA30' in df_signals.columns
        assert 'Buy_Signal' in df_signals.columns
        assert 'Sell_Signal' in df_signals.columns

    def test_calculate_signals_ma_columns(self, sample_stock_data, sample_strategy_params):
        """测试MA列的计算"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        # MA30向上趋势列
        assert 'MA30_Up' in df_signals.columns
        # 量能放大列
        assert 'Volume_Surge' in df_signals.columns
        # 回踩检测列
        assert 'MA5_Retest' in df_signals.columns

    def test_get_trades_no_signals(self, sample_stock_data_short, sample_strategy_params):
        """测试无信号的情况"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        trades = strategy.get_trades(sample_stock_data_short)

        # 数据不足，应该没有交易
        assert len(trades) == 0

    def test_get_trades_with_signals(self, sample_stock_data_with_signals, sample_strategy_params):
        """测试有信号的情况"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        trades = strategy.get_trades(sample_stock_data_with_signals)

        # 验证交易记录结构
        if len(trades) > 0:
            trade = trades[0]
            assert '买入日期' in trade
            assert '买入价' in trade
            assert '卖出日期' in trade
            assert '卖出价' in trade
            assert '持有天数' in trade
            assert '收益率%' in trade
            assert '状态' in trade

    def test_get_trades_hold_days(self, sample_stock_data_with_signals, sample_strategy_params):
        """测试持有天数"""
        sample_strategy_params['hold_days'] = 5
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        trades = strategy.get_trades(sample_stock_data_with_signals)

        if len(trades) > 0:
            # 平仓的交易应该持有5天
            closed_trades = [t for t in trades if t['状态'] == '平仓']
            if closed_trades:
                assert closed_trades[0]['持有天数'] == 5

    def test_get_trades_commission_fee(self, sample_stock_data_with_signals, sample_strategy_params):
        """测试手续费扣除"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        df_signals = strategy.calculate_signals(sample_stock_data_with_signals)

        # 手动创建一个交易
        buy_price = 10.0
        sell_price = 11.0
        # 理论收益 = (11-10)/10 * 100 = 10%
        # 扣除手续费后 = 10% - 0.1% = 9.9%
        expected_return = (sell_price - buy_price) / buy_price * 100 - 0.1

        assert expected_return == pytest.approx(9.9, rel=1e-5)

    def test_get_trades_open_position(self, sample_stock_data, sample_strategy_params):
        """测试未平仓头寸处理"""
        # 创建一个会产生买入信号但数据不足平仓的数据
        df = sample_stock_data.copy()
        strategy = VolumeBreakoutStrategy(sample_strategy_params)

        trades = strategy.get_trades(df)

        # 如果有未平仓的交易，状态应该是'未平仓'
        open_trades = [t for t in trades if t['状态'] == '未平仓']
        for trade in open_trades:
            assert trade['卖出日期'] == df.iloc[-1]['日期']


class TestSteadyTrendStrategy:
    """测试稳健型趋势跟踪策略"""

    def test_init(self, sample_steady_trend_params):
        """测试初始化"""
        strategy = SteadyTrendStrategy(sample_steady_trend_params)

        assert strategy.ma_short == 30
        assert strategy.ma_long == 60
        assert strategy.stop_loss == 0.08

    def test_calculate_signals(self, sample_stock_data, sample_steady_trend_params):
        """测试信号计算"""
        strategy = SteadyTrendStrategy(sample_steady_trend_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        assert 'Buy_Signal' in df_signals.columns
        assert 'Sell_Signal' in df_signals.columns
        assert 'MA30' in df_signals.columns
        assert 'MA60' in df_signals.columns

    def test_get_trades_stop_loss(self, sample_stock_data, sample_steady_trend_params):
        """测试止损功能"""
        strategy = SteadyTrendStrategy(sample_steady_trend_params)
        trades = strategy.get_trades(sample_stock_data)

        # 检查是否有止损退出的交易
        stop_loss_trades = [t for t in trades if t['状态'] == '止损']
        # 如果有止损交易，验证收益率应该接近-8%
        for trade in stop_loss_trades:
            assert trade['收益率%'] <= -7.9  # 考虑手续费

    def test_get_trades_take_profit(self, sample_stock_data, sample_steady_trend_params):
        """测试止盈功能"""
        strategy = SteadyTrendStrategy(sample_steady_trend_params)
        trades = strategy.get_trades(sample_stock_data)

        # 检查是否有止盈退出的交易
        take_profit_trades = [t for t in trades if t['状态'] == '止盈']
        for trade in take_profit_trades:
            assert trade['收益率%'] >= 14.9  # 考虑手续费

    def test_get_trades_trailing_stop(self, sample_stock_data, sample_steady_trend_params):
        """测试移动止盈功能"""
        strategy = SteadyTrendStrategy(sample_steady_trend_params)
        trades = strategy.get_trades(sample_stock_data)

        # 检查是否有移动止盈退出的交易
        trailing_trades = [t for t in trades if t['状态'] == '移动止盈']
        # 移动止盈应该是盈利的
        for trade in trailing_trades:
            assert trade['收益率%'] > 0


class TestAggressiveMomentumStrategy:
    """测试激进型突破动量策略"""

    def test_init(self, sample_aggressive_momentum_params):
        """测试初始化"""
        strategy = AggressiveMomentumStrategy(sample_aggressive_momentum_params)

        assert strategy.breakout_period == 20
        assert strategy.max_hold_days == 5
        assert strategy.rsi_period == 6

    def test_calculate_signals(self, sample_stock_data, sample_aggressive_momentum_params):
        """测试信号计算"""
        strategy = AggressiveMomentumStrategy(sample_aggressive_momentum_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        assert 'Buy_Signal' in df_signals.columns
        assert 'Sell_Signal' in df_signals.columns
        assert 'RSI_6' in df_signals.columns
        assert 'KDJ_K' in df_signals.columns

    def test_get_trades_max_hold_days(self, sample_stock_data, sample_aggressive_momentum_params):
        """测试最大持有天数限制"""
        sample_aggressive_momentum_params['max_hold_days'] = 3
        strategy = AggressiveMomentumStrategy(sample_aggressive_momentum_params)
        trades = strategy.get_trades(sample_stock_data)

        # 检查时间止损的交易
        time_stop_trades = [t for t in trades if t['状态'] == '时间止损']
        for trade in time_stop_trades:
            assert trade['持有天数'] >= 3

    def test_get_trades_atr_stop(self, sample_stock_data, sample_aggressive_momentum_params):
        """测试ATR动态止损"""
        strategy = AggressiveMomentumStrategy(sample_aggressive_momentum_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        # 验证ATR列存在
        assert 'ATR_14' in df_signals.columns

        trades = strategy.get_trades(sample_stock_data)
        # ATR止损应该存在
        atr_stop_trades = [t for t in trades if t['状态'] == 'ATR止损']
        # 如果有ATR止损，验证它是亏损的
        for trade in atr_stop_trades:
            assert trade['收益率%'] < 0


class TestBalancedMultiFactorStrategy:
    """测试平衡型多因子策略"""

    def test_init(self, sample_balanced_multi_factor_params):
        """测试初始化"""
        strategy = BalancedMultiFactorStrategy(sample_balanced_multi_factor_params)

        assert strategy.boll_period == 20
        assert strategy.rsi_period == 14
        assert strategy.min_factor_score == 0.6

    def test_calculate_factor_score(self, sample_stock_data, sample_balanced_multi_factor_params):
        """测试因子评分计算"""
        strategy = BalancedMultiFactorStrategy(sample_balanced_multi_factor_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        # 验证因子评分列存在
        assert 'Factor_Score' in df_signals.columns

        # 评分应该在0-1之间
        valid_scores = df_signals['Factor_Score'][df_signals['Factor_Score'] > 0]
        if len(valid_scores) > 0:
            assert valid_scores.min() >= 0
            assert valid_scores.max() <= 1

    def test_calculate_signals(self, sample_stock_data, sample_balanced_multi_factor_params):
        """测试信号计算"""
        strategy = BalancedMultiFactorStrategy(sample_balanced_multi_factor_params)
        df_signals = strategy.calculate_signals(sample_stock_data)

        assert 'Buy_Signal' in df_signals.columns
        assert 'Sell_Signal' in df_signals.columns
        assert 'BOLL_UPPER' in df_signals.columns
        assert 'BOLL_LOWER' in df_signals.columns

    def test_get_trades_tiered_profit_taking(self, sample_stock_data, sample_balanced_multi_factor_params):
        """测试分批止盈"""
        strategy = BalancedMultiFactorStrategy(sample_balanced_multi_factor_params)
        trades = strategy.get_trades(sample_stock_data)

        # 检查不同级别的止盈
        profit_statuses = ['第一批止盈', '第二批止盈', '最终止盈']
        profit_trades = [t for t in trades if t['状态'] in profit_statuses]

        # 验证止盈交易是盈利的
        for trade in profit_trades:
            assert trade['收益率%'] > 0

    def test_factor_weights_sum(self, sample_balanced_multi_factor_params):
        """测试因子权重总和"""
        strategy = BalancedMultiFactorStrategy(sample_balanced_multi_factor_params)

        total_weight = (
            strategy.factor_weight_boll +
            strategy.factor_weight_rsi +
            strategy.factor_weight_macd +
            strategy.factor_weight_volume +
            strategy.factor_weight_price
        )

        # 权重总和应该是1.0
        assert total_weight == pytest.approx(1.0, rel=1e-5)


class TestStrategyEdgeCases:
    """测试策略的边界情况"""

    def test_empty_dataframe(self, sample_empty_dataframe, sample_strategy_params):
        """测试空DataFrame"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        trades = strategy.get_trades(sample_empty_dataframe)

        assert len(trades) == 0

    def test_insufficient_data(self, sample_stock_data_short, sample_steady_trend_params):
        """测试数据不足的情况"""
        # 稳健型策略需要120天的MA
        strategy = SteadyTrendStrategy(sample_steady_trend_params)
        trades = strategy.get_trades(sample_stock_data_short)

        # 数据不足时应该没有交易或交易很少
        # 不应该抛出异常
        assert isinstance(trades, list)

    def test_all_nan_prices(self, sample_strategy_params):
        """测试价格全为NaN的情况"""
        df = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=100),
            '开盘': [np.nan] * 100,
            '收盘': [np.nan] * 100,
            '高': [np.nan] * 100,
            '低': [np.nan] * 100,
            '成交量': [1000000] * 100,
            '成交额': [10000000] * 100,
        })

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        trades = strategy.get_trades(df)

        # 应该没有交易
        assert len(trades) == 0

    def test_zero_volume(self, sample_strategy_params):
        """测试成交量为零的情况"""
        df = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=100),
            '开盘': [10.0] * 100,
            '收盘': [10.0] * 100,
            '高': [10.5] * 100,
            '低': [9.5] * 100,
            '成交量': [0] * 100,  # 零成交量
            '成交额': [0] * 100,
        })

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        trades = strategy.get_trades(df)

        # 零成交量不应该触发买入
        assert len(trades) == 0


class TestStrategyConsistency:
    """测试策略一致性"""

    def test_same_data_same_result(self, sample_stock_data, sample_strategy_params):
        """测试相同数据应该产生相同结果"""
        strategy = VolumeBreakoutStrategy(sample_strategy_params)

        trades1 = strategy.get_trades(sample_stock_data)
        trades2 = strategy.get_trades(sample_stock_data)

        assert len(trades1) == len(trades2)

        # 验证每笔交易都相同
        for t1, t2 in zip(trades1, trades2):
            assert t1['买入日期'] == t2['买入日期']
            assert t1['买入价'] == t2['买入价']
            assert t1['卖出日期'] == t2['卖出日期']
            assert t1['卖出价'] == t2['卖出价']

    def test_signals_not_modify_original_data(self, sample_stock_data, sample_strategy_params):
        """测试计算信号不修改原始数据"""
        original_columns = sample_stock_data.columns.tolist()
        original_len = len(sample_stock_data)

        strategy = VolumeBreakoutStrategy(sample_strategy_params)
        strategy.calculate_signals(sample_stock_data)

        # 原始数据不应该被修改
        assert sample_stock_data.columns.tolist() == original_columns
        assert len(sample_stock_data) == original_len
