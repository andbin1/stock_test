"""测试indicators.py - 技术指标计算模块"""
import pytest
import pandas as pd
import numpy as np
from indicators import (
    calculate_ma,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_kdj,
    calculate_bollinger_bands,
    calculate_atr,
    add_all_indicators,
)


class TestMovingAverage:
    """测试移动平均线计算"""

    def test_calculate_ma_basic(self, sample_stock_data):
        """测试基本的MA计算"""
        df = sample_stock_data
        ma5 = calculate_ma(df, 5)

        assert isinstance(ma5, pd.Series)
        assert len(ma5) == len(df)
        # 前4个值应该是NaN
        assert pd.isna(ma5.iloc[0:4]).all()
        # 第5个值应该是前5个收盘价的平均值
        assert ma5.iloc[4] == pytest.approx(df['收盘'].iloc[0:5].mean(), rel=1e-5)

    def test_calculate_ma_different_periods(self, sample_stock_data):
        """测试不同周期的MA"""
        df = sample_stock_data
        ma10 = calculate_ma(df, 10)
        ma20 = calculate_ma(df, 20)

        # MA10应该有更少的NaN值
        assert pd.isna(ma10).sum() < pd.isna(ma20).sum()

    def test_calculate_ma_with_custom_column(self, sample_stock_data):
        """测试使用自定义列"""
        df = sample_stock_data
        ma5_high = calculate_ma(df, 5, column='高')

        assert isinstance(ma5_high, pd.Series)
        assert ma5_high.iloc[4] == pytest.approx(df['高'].iloc[0:5].mean(), rel=1e-5)

    def test_calculate_ma_empty_data(self):
        """测试空数据"""
        df = pd.DataFrame({'收盘': []})
        ma5 = calculate_ma(df, 5)
        assert len(ma5) == 0


class TestEMA:
    """测试指数移动平均线"""

    def test_calculate_ema_basic(self, sample_stock_data):
        """测试基本的EMA计算"""
        df = sample_stock_data
        ema12 = calculate_ema(df, 12)

        assert isinstance(ema12, pd.Series)
        assert len(ema12) == len(df)
        # EMA的第一个值不应该是NaN（与MA不同）
        assert not pd.isna(ema12.iloc[11])

    def test_ema_vs_ma(self, sample_stock_data):
        """测试EMA和MA的差异"""
        df = sample_stock_data
        ema12 = calculate_ema(df, 12)
        ma12 = calculate_ma(df, 12)

        # EMA应该对近期价格更敏感
        # 两者不应该完全相同
        valid_idx = ~pd.isna(ma12)
        assert not np.allclose(ema12[valid_idx], ma12[valid_idx])


class TestMACD:
    """测试MACD指标"""

    def test_calculate_macd_basic(self, sample_stock_data):
        """测试基本的MACD计算"""
        df = sample_stock_data
        macd = calculate_macd(df)

        assert 'DIF' in macd
        assert 'DEA' in macd
        assert 'HIST' in macd

        assert isinstance(macd['DIF'], pd.Series)
        assert isinstance(macd['DEA'], pd.Series)
        assert isinstance(macd['HIST'], pd.Series)

        assert len(macd['DIF']) == len(df)
        assert len(macd['DEA']) == len(df)
        assert len(macd['HIST']) == len(df)

    def test_macd_relationship(self, sample_stock_data):
        """测试MACD组件之间的关系"""
        df = sample_stock_data
        macd = calculate_macd(df)

        # HIST应该等于DIF - DEA
        valid_idx = ~pd.isna(macd['HIST'])
        expected_hist = macd['DIF'][valid_idx] - macd['DEA'][valid_idx]
        assert np.allclose(macd['HIST'][valid_idx], expected_hist, rtol=1e-5)

    def test_macd_custom_params(self, sample_stock_data):
        """测试自定义MACD参数"""
        df = sample_stock_data
        macd = calculate_macd(df, fast=6, slow=12, signal=5)

        assert 'DIF' in macd
        assert not pd.isna(macd['DIF'].iloc[12])


class TestRSI:
    """测试RSI指标"""

    def test_calculate_rsi_basic(self, sample_stock_data):
        """测试基本的RSI计算"""
        df = sample_stock_data
        rsi14 = calculate_rsi(df, 14)

        assert isinstance(rsi14, pd.Series)
        assert len(rsi14) == len(df)

    def test_rsi_range(self, sample_stock_data):
        """测试RSI值范围（应该在0-100之间）"""
        df = sample_stock_data
        rsi14 = calculate_rsi(df, 14)

        valid_rsi = rsi14[~pd.isna(rsi14) & ~np.isinf(rsi14)]
        if len(valid_rsi) > 0:
            assert valid_rsi.min() >= 0
            assert valid_rsi.max() <= 100

    def test_rsi_different_periods(self, sample_stock_data):
        """测试不同周期的RSI"""
        df = sample_stock_data
        rsi6 = calculate_rsi(df, 6)
        rsi14 = calculate_rsi(df, 14)

        # 周期越短，信号越灵敏
        assert pd.isna(rsi6).sum() < pd.isna(rsi14).sum()


class TestKDJ:
    """测试KDJ指标"""

    def test_calculate_kdj_basic(self, sample_stock_data):
        """测试基本的KDJ计算"""
        df = sample_stock_data
        kdj = calculate_kdj(df)

        assert 'K' in kdj
        assert 'D' in kdj
        assert 'J' in kdj

        assert isinstance(kdj['K'], pd.Series)
        assert len(kdj['K']) == len(df)

    def test_kdj_relationship(self, sample_stock_data):
        """测试KDJ之间的关系: J = 3K - 2D"""
        df = sample_stock_data
        kdj = calculate_kdj(df)

        valid_idx = ~pd.isna(kdj['J'])
        expected_j = 3 * kdj['K'][valid_idx] - 2 * kdj['D'][valid_idx]
        assert np.allclose(kdj['J'][valid_idx], expected_j, rtol=1e-5)

    def test_kdj_custom_params(self, sample_stock_data):
        """测试自定义KDJ参数"""
        df = sample_stock_data
        kdj = calculate_kdj(df, n=5, m1=2, m2=2)

        assert 'K' in kdj
        assert 'D' in kdj
        assert 'J' in kdj


class TestBollingerBands:
    """测试布林带"""

    def test_calculate_bollinger_basic(self, sample_stock_data):
        """测试基本的布林带计算"""
        df = sample_stock_data
        boll = calculate_bollinger_bands(df, 20, 2.0)

        assert 'UPPER' in boll
        assert 'MIDDLE' in boll
        assert 'LOWER' in boll

        assert len(boll['UPPER']) == len(df)

    def test_bollinger_bands_relationship(self, sample_stock_data):
        """测试布林带上下轨关系"""
        df = sample_stock_data
        boll = calculate_bollinger_bands(df, 20, 2.0)

        valid_idx = ~pd.isna(boll['UPPER'])
        # 上轨应该大于中轨，中轨应该大于下轨
        assert (boll['UPPER'][valid_idx] >= boll['MIDDLE'][valid_idx]).all()
        assert (boll['MIDDLE'][valid_idx] >= boll['LOWER'][valid_idx]).all()

    def test_bollinger_middle_equals_ma(self, sample_stock_data):
        """测试布林带中轨应该等于移动平均线"""
        df = sample_stock_data
        boll = calculate_bollinger_bands(df, 20, 2.0)
        ma20 = calculate_ma(df, 20)

        valid_idx = ~pd.isna(ma20)
        assert np.allclose(boll['MIDDLE'][valid_idx], ma20[valid_idx], rtol=1e-5)


class TestATR:
    """测试ATR指标"""

    def test_calculate_atr_basic(self, sample_stock_data):
        """测试基本的ATR计算"""
        df = sample_stock_data
        atr14 = calculate_atr(df, 14)

        assert isinstance(atr14, pd.Series)
        assert len(atr14) == len(df)

    def test_atr_positive(self, sample_stock_data):
        """测试ATR值应该为正"""
        df = sample_stock_data
        atr14 = calculate_atr(df, 14)

        valid_atr = atr14[~pd.isna(atr14)]
        if len(valid_atr) > 0:
            assert (valid_atr >= 0).all()


class TestAddAllIndicators:
    """测试批量添加指标"""

    def test_add_all_indicators_default(self, sample_stock_data):
        """测试使用默认配置添加所有指标"""
        df = sample_stock_data
        df_with_indicators = add_all_indicators(df)

        # 检查是否添加了MA
        assert 'MA5' in df_with_indicators.columns
        assert 'MA10' in df_with_indicators.columns
        assert 'MA20' in df_with_indicators.columns

        # 检查是否添加了MACD
        assert 'MACD_DIF' in df_with_indicators.columns
        assert 'MACD_DEA' in df_with_indicators.columns
        assert 'MACD_HIST' in df_with_indicators.columns

        # 检查是否添加了RSI
        assert 'RSI_6' in df_with_indicators.columns
        assert 'RSI_14' in df_with_indicators.columns
        assert 'RSI_24' in df_with_indicators.columns

        # 检查是否添加了KDJ
        assert 'KDJ_K' in df_with_indicators.columns
        assert 'KDJ_D' in df_with_indicators.columns
        assert 'KDJ_J' in df_with_indicators.columns

        # 检查是否添加了布林带
        assert 'BOLL_UPPER' in df_with_indicators.columns
        assert 'BOLL_MIDDLE' in df_with_indicators.columns
        assert 'BOLL_LOWER' in df_with_indicators.columns

        # 检查是否添加了ATR
        assert 'ATR_14' in df_with_indicators.columns

        # 检查是否添加了成交量MA
        assert 'VOLUME_MA20' in df_with_indicators.columns

    def test_add_all_indicators_custom_config(self, sample_stock_data):
        """测试自定义配置"""
        df = sample_stock_data
        config = {
            'ma_periods': [5, 10],
            'macd': False,
            'rsi': True,
            'kdj': False,
            'bollinger': False,
            'atr': False,
        }
        df_with_indicators = add_all_indicators(df, config)

        # 只应该有MA5和MA10
        assert 'MA5' in df_with_indicators.columns
        assert 'MA10' in df_with_indicators.columns
        assert 'MA20' not in df_with_indicators.columns

        # 应该有RSI
        assert 'RSI_6' in df_with_indicators.columns

        # 不应该有MACD
        assert 'MACD_DIF' not in df_with_indicators.columns

        # 不应该有KDJ
        assert 'KDJ_K' not in df_with_indicators.columns

    def test_add_all_indicators_preserves_original(self, sample_stock_data):
        """测试添加指标不会修改原始数据"""
        df = sample_stock_data
        original_columns = df.columns.tolist()
        original_len = len(df)

        df_with_indicators = add_all_indicators(df)

        # 原始DataFrame不应该被修改
        assert df.columns.tolist() == original_columns
        assert len(df) == original_len

        # 新DataFrame应该包含更多列
        assert len(df_with_indicators.columns) > len(df.columns)
