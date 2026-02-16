"""
技术指标计算模块
提供常用技术指标的计算函数
"""
import pandas as pd
import numpy as np


def calculate_ma(df: pd.DataFrame, period: int, column: str = '收盘') -> pd.Series:
    """计算简单移动平均线"""
    return df[column].rolling(window=period).mean()


def calculate_ema(df: pd.DataFrame, period: int, column: str = '收盘') -> pd.Series:
    """计算指数移动平均线"""
    return df[column].ewm(span=period, adjust=False).mean()


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26,
                   signal: int = 9, column: str = '收盘') -> dict:
    """
    计算MACD指标
    返回: {'DIF': Series, 'DEA': Series, 'HIST': Series}
    """
    ema_fast = calculate_ema(df, fast, column)
    ema_slow = calculate_ema(df, slow, column)
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = dif - dea
    return {'DIF': dif, 'DEA': dea, 'HIST': hist}


def calculate_rsi(df: pd.DataFrame, period: int = 14,
                  column: str = '收盘') -> pd.Series:
    """
    计算RSI相对强弱指标
    """
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3,
                  m2: int = 3) -> dict:
    """
    计算KDJ指标
    返回: {'K': Series, 'D': Series, 'J': Series}
    """
    low_list = df['低'].rolling(window=n).min()
    high_list = df['高'].rolling(window=n).max()

    rsv = (df['收盘'] - low_list) / (high_list - low_list) * 100
    rsv = rsv.fillna(50)

    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d

    return {'K': k, 'D': d, 'J': j}


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20,
                               std_mult: float = 2.0,
                               column: str = '收盘') -> dict:
    """
    计算布林带
    返回: {'UPPER': Series, 'MIDDLE': Series, 'LOWER': Series}
    """
    middle = calculate_ma(df, period, column)
    std = df[column].rolling(window=period).std()
    upper = middle + (std * std_mult)
    lower = middle - (std * std_mult)
    return {'UPPER': upper, 'MIDDLE': middle, 'LOWER': lower}


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    计算ATR平均真实波幅
    """
    high_low = df['高'] - df['低']
    high_close = np.abs(df['高'] - df['收盘'].shift(1))
    low_close = np.abs(df['低'] - df['收盘'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def add_all_indicators(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    一次性添加所有常用指标到DataFrame
    config: 指标配置字典，如 {'ma_periods': [5, 10, 20, 30, 60], 'macd': True, ...}
    """
    df = df.copy()

    if config is None:
        config = {
            'ma_periods': [5, 10, 20, 30, 60, 120],
            'macd': True,
            'rsi': True,
            'kdj': True,
            'bollinger': True,
            'atr': True,
        }

    # 移动平均线
    for period in config.get('ma_periods', []):
        df[f'MA{period}'] = calculate_ma(df, period)

    # MACD
    if config.get('macd', True):
        macd = calculate_macd(df)
        df['MACD_DIF'] = macd['DIF']
        df['MACD_DEA'] = macd['DEA']
        df['MACD_HIST'] = macd['HIST']

    # RSI
    if config.get('rsi', True):
        df['RSI_6'] = calculate_rsi(df, 6)
        df['RSI_14'] = calculate_rsi(df, 14)
        df['RSI_24'] = calculate_rsi(df, 24)

    # KDJ
    if config.get('kdj', True):
        kdj = calculate_kdj(df)
        df['KDJ_K'] = kdj['K']
        df['KDJ_D'] = kdj['D']
        df['KDJ_J'] = kdj['J']

    # 布林带
    if config.get('bollinger', True):
        boll = calculate_bollinger_bands(df)
        df['BOLL_UPPER'] = boll['UPPER']
        df['BOLL_MIDDLE'] = boll['MIDDLE']
        df['BOLL_LOWER'] = boll['LOWER']

    # ATR
    if config.get('atr', True):
        df['ATR_14'] = calculate_atr(df, 14)

    # 成交量均线
    df['VOLUME_MA20'] = df['成交量'].rolling(window=20).mean()

    return df
