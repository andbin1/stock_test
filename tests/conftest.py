"""pytest配置文件和共享fixtures"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_stock_data():
    """创建示例股票数据用于测试"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    # 过滤掉周末
    dates = dates[dates.dayofweek < 5]

    n = len(dates)

    # 创建基础价格序列（带趋势）
    base_price = 10.0
    trend = np.linspace(0, 2, n)
    noise = np.random.randn(n) * 0.5
    close_prices = base_price + trend + noise
    close_prices = np.maximum(close_prices, 1.0)  # 确保价格为正

    df = pd.DataFrame({
        '日期': dates,
        '开盘': close_prices * (1 + np.random.randn(n) * 0.01),
        '收盘': close_prices,
        '高': close_prices * (1 + np.abs(np.random.randn(n) * 0.02)),
        '低': close_prices * (1 - np.abs(np.random.randn(n) * 0.02)),
        '成交量': np.random.randint(1000000, 10000000, n),
        '成交额': np.random.randint(10000000, 100000000, n),
        '振幅': np.random.uniform(1, 5, n),
        '涨跌幅': np.random.uniform(-3, 3, n),
        '涨跌': np.random.uniform(-0.5, 0.5, n),
        '换手率': np.random.uniform(0.5, 5, n),
    })

    return df


@pytest.fixture
def sample_stock_data_short():
    """创建短期股票数据（用于测试数据不足的情况）"""
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    dates = dates[dates.dayofweek < 5]

    n = len(dates)
    close_prices = 10.0 + np.random.randn(n) * 0.5

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

    return df


@pytest.fixture
def sample_stock_data_with_signals():
    """创建带有明确买卖信号的股票数据"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    dates = dates[dates.dayofweek < 5]

    n = len(dates)

    # 创建明确的上涨趋势
    close_prices = np.linspace(10, 15, n)

    # 创建明显的量能变化
    volume = np.ones(n) * 5000000
    volume[30:33] = 15000000  # 第30-32天量能放大
    volume[60:63] = 15000000  # 第60-62天量能放大

    df = pd.DataFrame({
        '日期': dates,
        '开盘': close_prices * 0.99,
        '收盘': close_prices,
        '高': close_prices * 1.02,
        '低': close_prices * 0.98,
        '成交量': volume,
        '成交额': volume * close_prices * 100,
        '振幅': np.ones(n) * 2.0,
        '涨跌幅': np.ones(n) * 1.0,
        '涨跌': np.ones(n) * 0.1,
        '换手率': np.ones(n) * 2.0,
    })

    return df


@pytest.fixture
def sample_empty_dataframe():
    """创建空的DataFrame"""
    return pd.DataFrame(columns=['日期', '开盘', '收盘', '高', '低', '成交量', '成交额'])


@pytest.fixture
def sample_strategy_params():
    """示例策略参数"""
    return {
        "ma_period": 30,
        "recent_days": 5,
        "retest_period": 5,
        "hold_days": 3,
        "volume_multiplier": 2.0,
        "turnover_min": 5.0,
        "turnover_max": 100.0,
    }


@pytest.fixture
def sample_steady_trend_params():
    """稳健型策略参数"""
    return {
        "ma_short": 30,
        "ma_long": 60,
        "ma_filter": 120,
        "volume_ma": 20,
        "volume_multiplier": 1.5,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "stop_loss": 0.08,
        "take_profit": 0.15,
        "trailing_stop": 0.05,
        "position_size": 0.20,
    }


@pytest.fixture
def sample_aggressive_momentum_params():
    """激进型策略参数"""
    return {
        "breakout_period": 20,
        "breakout_threshold": 0.03,
        "rsi_period": 6,
        "rsi_threshold": 50,
        "volume_multiplier": 2.5,
        "kdj_n": 5,
        "kdj_m1": 3,
        "kdj_m2": 3,
        "atr_period": 14,
        "atr_stop_mult": 2.0,
        "max_hold_days": 5,
        "trailing_stop": 0.03,
        "position_size": 0.15,
    }


@pytest.fixture
def sample_balanced_multi_factor_params():
    """平衡型策略参数"""
    return {
        "boll_period": 20,
        "boll_std": 2.0,
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "stop_loss": 0.10,
        "take_profit_1": 0.05,
        "take_profit_2": 0.10,
        "take_profit_final": 0.15,
        "factor_weight_boll": 0.20,
        "factor_weight_rsi": 0.25,
        "factor_weight_macd": 0.20,
        "factor_weight_volume": 0.15,
        "factor_weight_price": 0.20,
        "position_size": 0.20,
        "min_factor_score": 0.6,
    }


@pytest.fixture
def sample_trades():
    """示例交易记录"""
    return [
        {
            '买入日期': pd.Timestamp('2024-01-10'),
            '买入价': 10.0,
            '卖出日期': pd.Timestamp('2024-01-15'),
            '卖出价': 11.0,
            '持有天数': 5,
            '收益率%': 9.9,  # (11-10)/10 * 100 - 0.1
            '状态': '平仓',
        },
        {
            '买入日期': pd.Timestamp('2024-02-01'),
            '买入价': 12.0,
            '卖出日期': pd.Timestamp('2024-02-05'),
            '卖出价': 11.0,
            '持有天数': 4,
            '收益率%': -8.43,  # (11-12)/12 * 100 - 0.1
            '状态': '平仓',
        },
        {
            '买入日期': pd.Timestamp('2024-03-01'),
            '买入价': 11.5,
            '卖出日期': pd.Timestamp('2024-03-04'),
            '卖出价': 12.5,
            '持有天数': 3,
            '收益率%': 8.59,
            '状态': '平仓',
        },
    ]


@pytest.fixture
def sample_multiple_stocks_data(sample_stock_data):
    """多只股票数据"""
    return {
        '000001': sample_stock_data.copy(),
        '000002': sample_stock_data.copy(),
        '600000': sample_stock_data.copy(),
    }


@pytest.fixture
def mock_db_connection(mocker):
    """模拟数据库连接"""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor
