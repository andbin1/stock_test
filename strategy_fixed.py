"""修复的交易策略模块 - 解决同一天买卖的bug"""
import pandas as pd
import numpy as np
from indicators import add_all_indicators, calculate_rsi, calculate_kdj


class VolumeBreakoutStrategyFixed:
    """
    修复版本的量能突破回踩策略

    关键改进：
    1. 使用正确的持股天数计数（基于交易日，而不是行索引）
    2. 防止同一天的连续买卖
    3. 正确处理持仓状态管理
    """

    def __init__(self, params: dict):
        self.ma_period = params.get("ma_period", 30)
        self.recent_days = params.get("recent_days", 5)
        self.retest_period = params.get("retest_period", 5)
        self.hold_days = params.get("hold_days", 3)
        self.volume_multiplier = params.get("volume_multiplier", 2.0)
        self.volume_window = 3

        # 成交金额因子（单位：亿元）
        self.turnover_min = params.get("turnover_min", 5.0)
        self.turnover_max = params.get("turnover_max", 100.0)

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算交易信号"""
        df = df.copy()

        # 1. 计算均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA30'] = df['收盘'].rolling(window=self.ma_period).mean()

        # 2. 计算量能指标
        df['Recent3_Vol_Sum'] = df['成交量'].rolling(window=self.volume_window).sum()
        df['BaseVol_MA'] = df['成交量'].rolling(window=20).mean()

        # 3. 检查MA30向上趋势
        df['MA30_Up'] = df['MA30'] > df['MA30'].shift(1)

        # 4. 检查量能放大条件
        df['Volume_Surge'] = df['Recent3_Vol_Sum'] > (df['BaseVol_MA'] * self.volume_multiplier)

        # 5. 检查成交金额条件
        df['Turnover_Yi'] = df['成交额'] / 1e8
        df['Prev_Turnover_Yi'] = df['Turnover_Yi'].shift(1)
        df['Turnover_Check'] = (df['Prev_Turnover_Yi'] >= self.turnover_min) & (df['Prev_Turnover_Yi'] <= self.turnover_max)

        # 6. 检查5日线回踩
        df['MA5_Retest'] = (df['收盘'] < df['MA5']) & (df['收盘'] > df['MA5'] * 0.95)

        # 7. 综合买入信号
        df['Buy_Signal'] = df['MA30_Up'] & df['Volume_Surge'] & df['Turnover_Check'] & df['MA5_Retest']

        return df

    def get_trades(self, df: pd.DataFrame) -> list:
        """
        提取买卖点 - 修复版本

        关键改进：
        - 使用hold_counter追踪持股天数
        - 在第hold_days个交易日后卖出
        - 避免同一天连续买卖
        """
        df_signals = self.calculate_signals(df)
        trades = []

        buy_date = None
        buy_price = None
        buy_idx = None
        hold_counter = 0

        for i in range(len(df_signals)):
            row = df_signals.iloc[i]

            # 如果当前持仓，增加计数器
            if buy_date is not None:
                hold_counter += 1

            # 卖出条件1：达到持股天数
            if buy_date is not None and hold_counter >= self.hold_days:
                sell_date = row['日期']
                sell_price = row['收盘']

                profit_pct = (sell_price - buy_price) / buy_price * 100
                profit_pct_after_fee = profit_pct - 0.1

                trades.append({
                    '买入日期': buy_date,
                    '买入价': buy_price,
                    '卖出日期': sell_date,
                    '卖出价': sell_price,
                    '持有天数': hold_counter,
                    '收益率%': profit_pct_after_fee,
                    '状态': '平仓',
                })

                # 重置持仓
                buy_date = None
                buy_price = None
                buy_idx = None
                hold_counter = 0

            # 买入条件：没有持仓且有买入信号
            if row['Buy_Signal'] and buy_date is None:
                buy_date = row['日期']
                buy_price = row['收盘']
                buy_idx = i
                hold_counter = 0

        # 处理未平仓头寸
        if buy_date is not None:
            last_price = df_signals.iloc[-1]['收盘']
            profit_pct = (last_price - buy_price) / buy_price * 100
            profit_pct_after_fee = profit_pct - 0.1

            trades.append({
                '买入日期': buy_date,
                '买入价': buy_price,
                '卖出日期': df_signals.iloc[-1]['日期'],
                '卖出价': last_price,
                '持有天数': hold_counter,
                '收益率%': profit_pct_after_fee,
                '状态': '未平仓',
            })

        return trades


class SteadyTrendStrategy:
    """稳健型趋势跟踪策略 - 保持原有逻辑"""

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
    """激进型突破动量策略 - 保持原有逻辑"""

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
    """平衡型多因子策略 - 保持原有逻辑（代码略）"""

    def __init__(self, params: dict):
        self.boll_period = params.get("boll_period", 20)
        self.boll_std = params.get("boll_std", 2.0)
        self.rsi_period = params.get("rsi_period", 14)
        self.rsi_oversold = params.get("rsi_oversold", 30)
        self.rsi_overbought = params.get("rsi_overbought", 70)
        self.macd_fast = params.get("macd_fast", 12)
        self.macd_slow = params.get("macd_slow", 26)
        self.macd_signal = params.get("macd_signal", 9)
        self.stop_loss = params.get("stop_loss", 0.10)
        self.take_profit_1 = params.get("take_profit_1", 0.05)
        self.take_profit_2 = params.get("take_profit_2", 0.10)
        self.take_profit_final = params.get("take_profit_final", 0.15)
        self.factor_weight_boll = params.get("factor_weight_boll", 0.20)
        self.factor_weight_rsi = params.get("factor_weight_rsi", 0.25)
        self.factor_weight_macd = params.get("factor_weight_macd", 0.20)
        self.factor_weight_volume = params.get("factor_weight_volume", 0.15)
        self.factor_weight_price = params.get("factor_weight_price", 0.20)
        self.position_size = params.get("position_size", 0.20)
        self.min_factor_score = params.get("min_factor_score", 0.6)

    def calculate_factor_score(self, df: pd.DataFrame, idx: int) -> float:
        """计算多因子综合评分"""
        row = df.iloc[idx]
        scores = {}

        if 'BOLL_UPPER' in df.columns and 'BOLL_LOWER' in df.columns:
            boll_range = row['BOLL_UPPER'] - row['BOLL_LOWER']
            if boll_range > 0:
                boll_position = (row['收盘'] - row['BOLL_LOWER']) / boll_range
                scores['boll'] = (1 - boll_position) * self.factor_weight_boll
            else:
                scores['boll'] = 0
        else:
            scores['boll'] = 0

        rsi_col = f'RSI_{self.rsi_period}'
        if rsi_col in df.columns:
            if row[rsi_col] < self.rsi_oversold:
                rsi_score = (self.rsi_oversold - row[rsi_col]) / self.rsi_oversold
                scores['rsi'] = rsi_score * self.factor_weight_rsi
            else:
                scores['rsi'] = 0
        else:
            scores['rsi'] = 0

        if 'MACD_HIST' in df.columns:
            macd_positive = 1 if row['MACD_HIST'] > 0 else 0
            macd_increasing = 1 if idx > 0 and row['MACD_HIST'] > df.iloc[idx-1]['MACD_HIST'] else 0
            scores['macd'] = (macd_positive * 0.5 + macd_increasing * 0.5) * self.factor_weight_macd
        else:
            scores['macd'] = 0

        if idx >= 20 and 'VOLUME_MA20' in df.columns:
            volume_ma20 = df['成交量'].iloc[idx-20:idx].mean()
            volume_ratio = row['成交量'] / volume_ma20 if volume_ma20 > 0 else 0
            if 0.8 <= volume_ratio <= 1.5:
                scores['volume'] = self.factor_weight_volume
            else:
                scores['volume'] = 0
        else:
            scores['volume'] = 0

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

        df['Factor_Score'] = 0.0
        for i in range(len(df)):
            if i >= 20:
                df.loc[df.index[i], 'Factor_Score'] = self.calculate_factor_score(df, i)

        high_score = df['Factor_Score'] > self.min_factor_score
        near_lower = df['收盘'] < df['BOLL_LOWER'] * 1.02
        rsi_low = df[f'RSI_{self.rsi_period}'] < 40
        macd_positive = (df['MACD_HIST'] > 0) | (df['MACD_HIST'] > df['MACD_HIST'].shift(1))

        df['Buy_Signal'] = high_score & near_lower & rsi_low & macd_positive

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

                if profit_pct <= -self.stop_loss:
                    sell_reason = '止损'

                elif profit_pct >= self.take_profit_final:
                    sell_reason = '最终止盈'

                elif profit_pct >= self.take_profit_2:
                    sell_reason = '第二批止盈'

                elif profit_pct >= self.take_profit_1:
                    sell_reason = '第一批止盈'

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
    from config import STRATEGY_PARAMS
    from data_fetcher import get_stock_data

    df = get_stock_data("000001", "20240101", "20250213")
    if df is not None:
        strategy = VolumeBreakoutStrategyFixed(STRATEGY_PARAMS)
        signals = strategy.calculate_signals(df)
        trades = strategy.get_trades(df)

        print("\n=== 交易记录 ===")
        trades_df = pd.DataFrame(trades)
        print(trades_df)
        print(f"\n总交易数: {len(trades)}")
        if trades:
            print(f"平均收益率: {trades_df['收益率%'].mean():.2f}%")
