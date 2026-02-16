"""交易策略模块 - 实现用户指定的策略"""
import pandas as pd
import numpy as np
from indicators import add_all_indicators, calculate_rsi, calculate_kdj


class VolumeBreakoutStrategy:
    """
    策略逻辑：
    1. 30日均线向上（MA30 > MA30前一天）
    2. 量能放大（最近3个交易日总成交量 > 3个交易日前的平均成交量 * 倍数）
    3. 上一交易日成交金额在配置区间内
    4. 股价回踩5日线（收盘价 < MA5）
    5. 3个交易日后卖出
    """

    def __init__(self, params: dict):
        self.ma_period = params.get("ma_period", 30)
        self.recent_days = params.get("recent_days", 5)  # 用于参考，不直接用于量能计算
        self.retest_period = params.get("retest_period", 5)
        self.hold_days = params.get("hold_days", 3)
        self.volume_multiplier = params.get("volume_multiplier", 2.0)
        self.volume_window = 3  # 最近3个交易日的总成交量

        # 成交金额因子（单位：亿元）
        self.turnover_min = params.get("turnover_min", 5.0)  # 最小成交金额（亿）
        self.turnover_max = params.get("turnover_max", 100.0)  # 最大成交金额（亿）

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算交易信号"""
        df = df.copy()

        # 1. 计算均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA30'] = df['收盘'].rolling(window=self.ma_period).mean()

        # 2. 计算量能指标
        # 最近3个交易日的总成交量
        df['Recent3_Vol_Sum'] = df['成交量'].rolling(window=self.volume_window).sum()
        # 3个交易日前往前20日的平均成交量（作为基准）
        df['BaseVol_MA'] = df['成交量'].rolling(window=20).mean()

        # 3. 检查MA30向上趋势
        df['MA30_Up'] = df['MA30'] > df['MA30'].shift(1)

        # 4. 检查量能放大条件：最近3日总成交量 > 3日前平均成交量 * 倍数
        df['Volume_Surge'] = df['Recent3_Vol_Sum'] > (df['BaseVol_MA'] * self.volume_multiplier)

        # 5. 检查上一交易日成交金额（单位：亿）
        # 成交额已经在单位元，需要转换为亿（1亿 = 1e8）
        df['Turnover_Yi'] = df['成交额'] / 1e8
        df['Prev_Turnover_Yi'] = df['Turnover_Yi'].shift(1)
        df['Turnover_Check'] = (df['Prev_Turnover_Yi'] >= self.turnover_min) & (df['Prev_Turnover_Yi'] <= self.turnover_max)

        # 6. 检查5日线回踩：收盘价 < MA5，且收盘价 > MA5 * 0.95（不能跌太深）
        df['MA5_Retest'] = (df['收盘'] < df['MA5']) & (df['收盘'] > df['MA5'] * 0.95)

        # 7. 综合买入信号：四个条件同时满足
        df['Buy_Signal'] = df['MA30_Up'] & df['Volume_Surge'] & df['Turnover_Check'] & df['MA5_Retest']

        # 标记买入后的卖出日期（3个交易日后）
        df['Sell_Signal'] = False
        for i in range(len(df)):
            if df.loc[i, 'Buy_Signal']:
                if i + self.hold_days < len(df):
                    df.loc[i + self.hold_days, 'Sell_Signal'] = True

        return df

    def get_trades(self, df: pd.DataFrame) -> list:
        """提取买卖点"""
        df_signals = self.calculate_signals(df)
        trades = []

        buy_date = None
        buy_price = None
        buy_idx = None

        for i, row in df_signals.iterrows():
            if row['Buy_Signal'] and buy_date is None:
                buy_date = row['日期']
                buy_price = row['收盘']
                buy_idx = i

            if row['Sell_Signal'] and buy_date is not None:
                sell_date = row['日期']
                sell_price = row['收盘']

                # 计算收益
                profit_pct = (sell_price - buy_price) / buy_price * 100
                profit_pct_after_fee = profit_pct - 0.1  # 手续费往返0.1%

                trades.append({
                    '买入日期': buy_date,
                    '买入价': buy_price,
                    '卖出日期': sell_date,
                    '卖出价': sell_price,
                    '持有天数': self.hold_days,
                    '收益率%': profit_pct_after_fee,
                    '状态': '平仓',
                })

                buy_date = None
                buy_price = None
                buy_idx = None

        # 处理未平仓的头寸（用最后一日价格）
        if buy_date is not None:
            last_price = df_signals.iloc[-1]['收盘']
            profit_pct = (last_price - buy_price) / buy_price * 100
            profit_pct_after_fee = profit_pct - 0.1

            trades.append({
                '买入日期': buy_date,
                '买入价': buy_price,
                '卖出日期': df_signals.iloc[-1]['日期'],
                '卖出价': last_price,
                '持有天数': len(df_signals) - buy_idx - 1,
                '收益率%': profit_pct_after_fee,
                '状态': '未平仓',
            })

        return trades


class SteadyTrendStrategy:
    """
    稳健型趋势跟踪策略
    适合：主板蓝筹股（沪深300成分股）
    特点：低频交易、趋势跟随、严格风控
    """

    def __init__(self, params: dict):
        # 均线参数
        self.ma_short = params.get("ma_short", 30)
        self.ma_long = params.get("ma_long", 60)
        self.ma_filter = params.get("ma_filter", 120)

        # 量能参数
        self.volume_ma = params.get("volume_ma", 20)
        self.volume_multiplier = params.get("volume_multiplier", 1.5)

        # MACD参数
        self.macd_fast = params.get("macd_fast", 12)
        self.macd_slow = params.get("macd_slow", 26)
        self.macd_signal = params.get("macd_signal", 9)

        # 止损止盈
        self.stop_loss = params.get("stop_loss", 0.08)
        self.take_profit = params.get("take_profit", 0.15)
        self.trailing_stop = params.get("trailing_stop", 0.05)

        # 仓位管理
        self.position_size = params.get("position_size", 0.20)

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算买卖信号"""
        df = add_all_indicators(df, {
            'ma_periods': [self.ma_short, self.ma_long, self.ma_filter],
            'macd': True,
            'rsi': False,
            'kdj': False,
            'bollinger': False,
            'atr': False,
        })

        # 买入条件
        trend_up = df['收盘'] > df[f'MA{self.ma_filter}']
        golden_cross = (df[f'MA{self.ma_short}'] > df[f'MA{self.ma_long}']) & \
                      (df[f'MA{self.ma_short}'].shift(1) <= df[f'MA{self.ma_long}'].shift(1))
        volume_surge = df['成交量'] > df['VOLUME_MA20'] * self.volume_multiplier
        macd_cross = (df['MACD_DIF'] > df['MACD_DEA']) & \
                    (df['MACD_DIF'].shift(1) <= df['MACD_DEA'].shift(1))

        df['Buy_Signal'] = trend_up & golden_cross & volume_surge & macd_cross

        # 卖出条件
        death_cross = (df[f'MA{self.ma_short}'] < df[f'MA{self.ma_long}']) & \
                     (df[f'MA{self.ma_short}'].shift(1) >= df[f'MA{self.ma_long}'].shift(1))
        df['Sell_Signal'] = death_cross

        return df

    def get_trades(self, df: pd.DataFrame) -> list:
        """提取交易记录"""
        df_signals = self.calculate_signals(df)
        trades = []

        position = None

        for i in range(len(df_signals)):
            row = df_signals.iloc[i]

            # 买入逻辑
            if row['Buy_Signal'] and position is None:
                position = {
                    'buy_date': row['日期'],
                    'buy_price': row['收盘'],
                    'highest_price': row['收盘'],
                }
                continue

            # 持仓期间更新最高价
            if position is not None:
                position['highest_price'] = max(position['highest_price'], row['收盘'])

                current_price = row['收盘']
                entry_price = position['buy_price']
                profit_pct = (current_price - entry_price) / entry_price

                sell_reason = None

                # 止损
                if profit_pct <= -self.stop_loss:
                    sell_reason = '止损'

                # 固定止盈
                elif profit_pct >= self.take_profit:
                    sell_reason = '止盈'

                # 移动止盈
                elif current_price < position['highest_price'] * (1 - self.trailing_stop):
                    sell_reason = '移动止盈'

                # 死叉卖出
                elif row['Sell_Signal']:
                    sell_reason = '死叉'

                # 执行卖出
                if sell_reason:
                    hold_days = (row['日期'] - position['buy_date']).days
                    profit = (current_price - entry_price) / entry_price * 100 - 0.1

                    trades.append({
                        '买入日期': position['buy_date'],
                        '买入价': position['buy_price'],
                        '卖出日期': row['日期'],
                        '卖出价': current_price,
                        '持有天数': hold_days,
                        '收益率%': profit,
                        '状态': sell_reason,
                    })

                    position = None

        return trades


class AggressiveMomentumStrategy:
    """
    激进型突破动量策略
    适合：创业板、科创板高成长股
    特点：高频交易、快进快出、动量驱动
    """

    def __init__(self, params: dict):
        # 突破参数
        self.breakout_period = params.get("breakout_period", 20)
        self.breakout_threshold = params.get("breakout_threshold", 0.03)

        # RSI参数
        self.rsi_period = params.get("rsi_period", 6)
        self.rsi_threshold = params.get("rsi_threshold", 50)

        # 量能参数
        self.volume_multiplier = params.get("volume_multiplier", 2.5)

        # KDJ参数
        self.kdj_n = params.get("kdj_n", 5)
        self.kdj_m1 = params.get("kdj_m1", 3)
        self.kdj_m2 = params.get("kdj_m2", 3)

        # ATR参数
        self.atr_period = params.get("atr_period", 14)
        self.atr_stop_mult = params.get("atr_stop_mult", 2.0)

        # 持仓控制
        self.max_hold_days = params.get("max_hold_days", 5)
        self.trailing_stop = params.get("trailing_stop", 0.03)

        # 仓位管理
        self.position_size = params.get("position_size", 0.15)

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算买卖信号"""
        df = add_all_indicators(df, {
            'ma_periods': [],
            'macd': False,
            'rsi': True,
            'kdj': True,
            'bollinger': False,
            'atr': True,
        })

        # 突破条件
        high_n = df['高'].rolling(window=self.breakout_period).max().shift(1)
        breakout = df['收盘'] > high_n * (1 + self.breakout_threshold)

        # 量能放大
        volume_surge = df['成交量'] > df['VOLUME_MA20'] * self.volume_multiplier

        # RSI强势
        rsi_strong = df[f'RSI_{self.rsi_period}'] > self.rsi_threshold

        # KDJ金叉
        kdj_cross = (df['KDJ_K'] > df['KDJ_D']) & \
                   (df['KDJ_K'].shift(1) <= df['KDJ_D'].shift(1))
        kdj_valid = df['KDJ_K'] > 20

        df['Buy_Signal'] = breakout & volume_surge & rsi_strong & kdj_cross & kdj_valid

        # KDJ死叉
        kdj_death = (df['KDJ_K'] < df['KDJ_D']) & \
                   (df['KDJ_K'].shift(1) >= df['KDJ_D'].shift(1)) & \
                   (df['KDJ_J'] > 80)
        df['Sell_Signal'] = kdj_death

        return df

    def get_trades(self, df: pd.DataFrame) -> list:
        """提取交易记录"""
        df_signals = self.calculate_signals(df)
        trades = []

        position = None

        for i in range(len(df_signals)):
            row = df_signals.iloc[i]

            if row['Buy_Signal'] and position is None:
                position = {
                    'buy_date': row['日期'],
                    'buy_price': row['收盘'],
                    'highest_price': row['收盘'],
                }
                continue

            if position is not None:
                position['highest_price'] = max(position['highest_price'], row['收盘'])

                current_price = row['收盘']
                entry_price = position['buy_price']
                atr = row['ATR_14'] if 'ATR_14' in df_signals.columns else 0
                hold_days = (row['日期'] - position['buy_date']).days

                sell_reason = None

                # ATR动态止损
                if atr > 0:
                    atr_stop = entry_price - (atr * self.atr_stop_mult)
                    if current_price <= atr_stop:
                        sell_reason = 'ATR止损'

                # 时间止损
                if sell_reason is None and hold_days >= self.max_hold_days:
                    sell_reason = '时间止损'

                # KDJ死叉
                if sell_reason is None and row['Sell_Signal']:
                    sell_reason = 'KDJ死叉'

                # 移动止盈
                if sell_reason is None and current_price < position['highest_price'] * (1 - self.trailing_stop):
                    sell_reason = '移动止盈'

                if sell_reason:
                    profit = (current_price - entry_price) / entry_price * 100 - 0.1

                    trades.append({
                        '买入日期': position['buy_date'],
                        '买入价': position['buy_price'],
                        '卖出日期': row['日期'],
                        '卖出价': current_price,
                        '持有天数': hold_days,
                        '收益率%': profit,
                        '状态': sell_reason,
                    })

                    position = None

        return trades


class BalancedMultiFactorStrategy:
    """
    平衡型多因子策略
    适合：中证500成分股、震荡市场
    特点：多因子评分、分批建仓、智能止盈
    """

    def __init__(self, params: dict):
        # 布林带参数
        self.boll_period = params.get("boll_period", 20)
        self.boll_std = params.get("boll_std", 2.0)

        # RSI参数
        self.rsi_period = params.get("rsi_period", 14)
        self.rsi_oversold = params.get("rsi_oversold", 30)
        self.rsi_overbought = params.get("rsi_overbought", 70)

        # MACD参数
        self.macd_fast = params.get("macd_fast", 12)
        self.macd_slow = params.get("macd_slow", 26)
        self.macd_signal = params.get("macd_signal", 9)

        # 止损止盈
        self.stop_loss = params.get("stop_loss", 0.10)
        self.take_profit_1 = params.get("take_profit_1", 0.05)
        self.take_profit_2 = params.get("take_profit_2", 0.10)
        self.take_profit_final = params.get("take_profit_final", 0.15)

        # 因子权重
        self.factor_weight_boll = params.get("factor_weight_boll", 0.20)
        self.factor_weight_rsi = params.get("factor_weight_rsi", 0.25)
        self.factor_weight_macd = params.get("factor_weight_macd", 0.20)
        self.factor_weight_volume = params.get("factor_weight_volume", 0.15)
        self.factor_weight_price = params.get("factor_weight_price", 0.20)

        # 仓位管理
        self.position_size = params.get("position_size", 0.20)
        self.min_factor_score = params.get("min_factor_score", 0.6)

    def calculate_factor_score(self, df: pd.DataFrame, idx: int) -> float:
        """计算多因子综合评分"""
        row = df.iloc[idx]
        scores = {}

        # 因子1：布林带位置
        if 'BOLL_UPPER' in df.columns and 'BOLL_LOWER' in df.columns:
            boll_range = row['BOLL_UPPER'] - row['BOLL_LOWER']
            if boll_range > 0:
                boll_position = (row['收盘'] - row['BOLL_LOWER']) / boll_range
                scores['boll'] = (1 - boll_position) * self.factor_weight_boll
            else:
                scores['boll'] = 0
        else:
            scores['boll'] = 0

        # 因子2：RSI超卖
        rsi_col = f'RSI_{self.rsi_period}'
        if rsi_col in df.columns:
            if row[rsi_col] < self.rsi_oversold:
                rsi_score = (self.rsi_oversold - row[rsi_col]) / self.rsi_oversold
                scores['rsi'] = rsi_score * self.factor_weight_rsi
            else:
                scores['rsi'] = 0
        else:
            scores['rsi'] = 0

        # 因子3：MACD趋势
        if 'MACD_HIST' in df.columns:
            macd_positive = 1 if row['MACD_HIST'] > 0 else 0
            macd_increasing = 1 if idx > 0 and row['MACD_HIST'] > df.iloc[idx-1]['MACD_HIST'] else 0
            scores['macd'] = (macd_positive * 0.5 + macd_increasing * 0.5) * self.factor_weight_macd
        else:
            scores['macd'] = 0

        # 因子4：量能健康度
        if idx >= 20 and 'VOLUME_MA20' in df.columns:
            volume_ma20 = df['成交量'].iloc[idx-20:idx].mean()
            volume_ratio = row['成交量'] / volume_ma20 if volume_ma20 > 0 else 0
            if 0.8 <= volume_ratio <= 1.5:
                scores['volume'] = self.factor_weight_volume
            else:
                scores['volume'] = 0
        else:
            scores['volume'] = 0

        # 因子5：价格位置
        if idx >= 20:
            low_20 = df['低'].iloc[idx-20:idx].min()
            high_20 = df['高'].iloc[idx-20:idx].max()
            if high_20 > low_20:
                price_position = (row['收盘'] - low_20) / (high_20 - low_20)
                scores['price'] = (1 - price_position) * self.factor_weight_price
            else:
                scores['price'] = 0
        else:
            scores['price'] = 0

        total_score = sum(scores.values())
        return total_score

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算买卖信号"""
        df = add_all_indicators(df, {
            'ma_periods': [],
            'macd': True,
            'rsi': True,
            'kdj': False,
            'bollinger': True,
            'atr': False,
        })

        # 计算每行的因子评分
        df['Factor_Score'] = 0.0
        for i in range(len(df)):
            if i >= 20:
                df.loc[df.index[i], 'Factor_Score'] = self.calculate_factor_score(df, i)

        # 买入条件
        high_score = df['Factor_Score'] > self.min_factor_score
        near_lower = df['收盘'] < df['BOLL_LOWER'] * 1.02
        rsi_low = df[f'RSI_{self.rsi_period}'] < 40
        macd_positive = (df['MACD_HIST'] > 0) | (df['MACD_HIST'] > df['MACD_HIST'].shift(1))

        df['Buy_Signal'] = high_score & near_lower & rsi_low & macd_positive

        # 卖出条件
        near_upper = df['收盘'] > df['BOLL_UPPER'] * 0.98
        rsi_high = df[f'RSI_{self.rsi_period}'] > self.rsi_overbought
        df['Sell_Signal'] = near_upper | rsi_high

        return df

    def get_trades(self, df: pd.DataFrame) -> list:
        """提取交易记录"""
        df_signals = self.calculate_signals(df)
        trades = []

        position = None

        for i in range(len(df_signals)):
            row = df_signals.iloc[i]

            if row['Buy_Signal'] and position is None:
                position = {
                    'buy_date': row['日期'],
                    'buy_price': row['收盘'],
                    'highest_price': row['收盘'],
                }
                continue

            if position is not None:
                position['highest_price'] = max(position['highest_price'], row['收盘'])

                current_price = row['收盘']
                entry_price = position['buy_price']
                profit_pct = (current_price - entry_price) / entry_price

                sell_reason = None

                # 止损
                if profit_pct <= -self.stop_loss:
                    sell_reason = '止损'

                # 分批止盈
                elif profit_pct >= self.take_profit_final:
                    sell_reason = '最终止盈'

                elif profit_pct >= self.take_profit_2:
                    sell_reason = '第二批止盈'

                elif profit_pct >= self.take_profit_1:
                    sell_reason = '第一批止盈'

                # 技术信号卖出
                elif row['Sell_Signal']:
                    sell_reason = '技术信号'

                if sell_reason:
                    hold_days = (row['日期'] - position['buy_date']).days
                    profit = (current_price - entry_price) / entry_price * 100 - 0.1

                    trades.append({
                        '买入日期': position['buy_date'],
                        '买入价': position['buy_price'],
                        '卖出日期': row['日期'],
                        '卖出价': current_price,
                        '持有天数': hold_days,
                        '收益率%': profit,
                        '状态': sell_reason,
                    })

                    position = None

        return trades


if __name__ == "__main__":
    # 测试策略
    from config import STRATEGY_PARAMS
    from data_fetcher import get_stock_data

    df = get_stock_data("000001", "20240101", "20250213")
    if df is not None:
        strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
        signals = strategy.calculate_signals(df)
        trades = strategy.get_trades(df)

        print("\n=== 信号检验 ===")
        print(signals[signals['Buy_Signal'] | signals['Sell_Signal']][
            ['日期', '收盘', 'MA5', 'MA30', 'MA30_Up', 'Volume_Surge', 'MA5_Retest', 'Buy_Signal', 'Sell_Signal']
        ])

        print("\n=== 交易记录 ===")
        trades_df = pd.DataFrame(trades)
        print(trades_df)
        print(f"\n总交易数: {len(trades)}")
        if trades:
            print(f"平均收益率: {trades_df['收益率%'].mean():.2f}%")
