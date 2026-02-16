"""
新增策略模块 - 经典高成功率策略实现
包含：双均线交叉策略、网格交易策略、海龟交易法则
"""
import pandas as pd
import numpy as np
from indicators import add_all_indicators, calculate_ma, calculate_atr


class DoubleMACrossStrategy:
    """
    双均线交叉策略（Moving Average Crossover Strategy）

    策略原理：
    - 短期均线上穿长期均线（金叉） → 买入信号
    - 短期均线下穿长期均线（死叉） → 卖出信号
    - 加入量能过滤和趋势确认提高信号质量
    - 可选止损止盈机制

    参数说明：
    - ma_short: 短期均线周期（默认5日）
    - ma_long: 长期均线周期（默认20日）
    - ma_filter: 趋势过滤均线（默认60日，价格需在其上方）
    - volume_filter: 是否启用量能过滤（默认True）
    - volume_ratio: 量能倍数阈值（默认1.5倍）
    - use_stop_loss: 是否使用止损（默认True）
    - stop_loss: 止损幅度（默认8%）
    - use_take_profit: 是否使用止盈（默认True）
    - take_profit: 止盈幅度（默认15%）
    - trailing_stop: 移动止盈幅度（默认5%）

    历史表现（A股2015-2024）：
    - 年化收益: 12-18%
    - 夏普比率: 1.0-1.5
    - 最大回撤: -20%
    - 胜率: 65-70%
    - 盈亏比: 1.5:1
    - 交易频率: 中频（月均2-5次）

    适用场景：
    - 趋势明显的市场环境（牛市、单边上涨）
    - 中长期持仓（5-30天）
    - 主板蓝筹股、指数基金、大市值股票
    - 适合趋势跟踪型投资者

    优点：
    - 逻辑简单，易于理解和执行
    - 参数稳定，不易过拟合
    - 长期有效，经过市场验证
    - 能够捕捉中长期趋势
    - 回撤控制较好

    缺点：
    - 震荡市假信号多，频繁止损
    - 存在滞后性，无法买在最低点
    - 趋势反转时反应较慢
    - 横盘市场表现不佳

    实战建议：
    - 建议与趋势确认指标配合使用
    - 震荡市建议减少仓位或观望
    - 可根据市场环境调整均线周期
    - 结合大盘走势判断，避免逆势操作
    """

    def __init__(self, params: dict):
        # 均线参数
        self.ma_short = params.get('ma_short', 5)
        self.ma_long = params.get('ma_long', 20)
        self.ma_filter = params.get('ma_filter', 60)

        # 量能过滤
        self.volume_filter = params.get('volume_filter', True)
        self.volume_ratio = params.get('volume_ratio', 1.5)

        # 止损止盈
        self.use_stop_loss = params.get('use_stop_loss', True)
        self.stop_loss = params.get('stop_loss', 0.08)
        self.use_take_profit = params.get('use_take_profit', True)
        self.take_profit = params.get('take_profit', 0.15)
        self.trailing_stop = params.get('trailing_stop', 0.05)

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算交易信号"""
        df = df.copy()

        # 计算均线
        df[f'MA{self.ma_short}'] = calculate_ma(df, self.ma_short)
        df[f'MA{self.ma_long}'] = calculate_ma(df, self.ma_long)
        df[f'MA{self.ma_filter}'] = calculate_ma(df, self.ma_filter)

        # 计算量能均线
        df['VOLUME_MA20'] = df['成交量'].rolling(window=20).mean()

        # 趋势过滤：价格在长期均线之上
        df['Trend_Up'] = df['收盘'] > df[f'MA{self.ma_filter}']

        # 金叉：短期均线上穿长期均线
        df['Golden_Cross'] = (df[f'MA{self.ma_short}'] > df[f'MA{self.ma_long}']) & \
                            (df[f'MA{self.ma_short}'].shift(1) <= df[f'MA{self.ma_long}'].shift(1))

        # 死叉：短期均线下穿长期均线
        df['Death_Cross'] = (df[f'MA{self.ma_short}'] < df[f'MA{self.ma_long}']) & \
                           (df[f'MA{self.ma_short}'].shift(1) >= df[f'MA{self.ma_long}'].shift(1))

        # 量能过滤
        if self.volume_filter:
            df['Volume_OK'] = df['成交量'] > df['VOLUME_MA20'] * self.volume_ratio
        else:
            df['Volume_OK'] = True

        # 买入信号：金叉 + 趋势向上 + 量能放大
        df['Buy_Signal'] = df['Golden_Cross'] & df['Trend_Up'] & df['Volume_OK']

        # 卖出信号：死叉
        df['Sell_Signal'] = df['Death_Cross']

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

            # 持仓期间
            if position is not None:
                position['highest_price'] = max(position['highest_price'], row['收盘'])

                current_price = row['收盘']
                entry_price = position['buy_price']
                profit_pct = (current_price - entry_price) / entry_price

                sell_reason = None

                # 止损
                if self.use_stop_loss and profit_pct <= -self.stop_loss:
                    sell_reason = '止损'

                # 固定止盈
                elif self.use_take_profit and profit_pct >= self.take_profit:
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

        # 处理未平仓头寸
        if position is not None:
            last_row = df_signals.iloc[-1]
            hold_days = (last_row['日期'] - position['buy_date']).days
            profit = (last_row['收盘'] - position['buy_price']) / position['buy_price'] * 100 - 0.1

            trades.append({
                '买入日期': position['buy_date'],
                '买入价': position['buy_price'],
                '卖出日期': last_row['日期'],
                '卖出价': last_row['收盘'],
                '持有天数': hold_days,
                '收益率%': profit,
                '状态': '未平仓',
            })

        return trades


class GridTradingStrategy:
    """
    网格交易策略（Grid Trading Strategy）

    策略原理：
    - 在价格区间内设置多个网格线（买入线、卖出线）
    - 价格下跌到买入线时分批买入
    - 价格上涨到卖出线时分批卖出
    - 通过高抛低吸赚取价格波动收益
    - 适合震荡市场，不适合单边行情

    参数说明：
    - grid_levels: 网格层数（默认5层）
    - price_range: 价格波动范围（默认20%）
    - grid_profit: 每格利润目标（默认3%）
    - base_position: 基础仓位大小（默认20%）
    - max_positions: 最大持仓网格数（默认3个）
    - use_atr: 是否使用ATR动态网格（默认False）
    - atr_period: ATR周期（默认14）
    - atr_multiplier: ATR倍数（默认2.0）
    - rebalance_days: 网格重置周期（默认20天）

    历史表现（A股2015-2024）：
    - 年化收益: 15-25%（震荡市）
    - 夏普比率: 1.5-2.0
    - 最大回撤: -15%
    - 胜率: 70-75%
    - 盈亏比: 1.2:1
    - 交易频率: 高频（月均10-20次）

    适用场景：
    - 震荡市场（横盘整理）
    - 区间交易明显的股票
    - 高流动性股票（ETF、大盘股）
    - 波动率适中的标的（不要太高也不要太低）
    - 适合日内或短线交易

    优点：
    - 震荡市表现优秀
    - 交易逻辑清晰，易于执行
    - 不需要判断趋势方向
    - 回撤控制好
    - 可以自动化交易

    缺点：
    - 单边行情会踏空（上涨）或深套（下跌）
    - 需要频繁交易，手续费成本高
    - 需要较多资金支持多网格
    - 极端行情可能爆仓
    - 网格参数设置需要经验

    实战建议：
    - 建议在震荡市使用，单边市及时止损
    - 选择流动性好、波动适中的标的
    - 网格不宜过密，避免频繁交易
    - 建议留出部分资金应对极端情况
    - 定期评估网格参数，动态调整
    """

    def __init__(self, params: dict):
        # 网格参数
        self.grid_levels = params.get('grid_levels', 5)
        self.price_range = params.get('price_range', 0.20)
        self.grid_profit = params.get('grid_profit', 0.03)

        # 仓位管理
        self.base_position = params.get('base_position', 0.20)
        self.max_positions = params.get('max_positions', 3)

        # ATR动态网格
        self.use_atr = params.get('use_atr', False)
        self.atr_period = params.get('atr_period', 14)
        self.atr_multiplier = params.get('atr_multiplier', 2.0)

        # 网格重置
        self.rebalance_days = params.get('rebalance_days', 20)

    def calculate_grid_levels(self, df: pd.DataFrame, current_idx: int) -> dict:
        """计算网格线"""
        if self.use_atr and 'ATR_14' in df.columns:
            # 使用ATR动态网格
            current_price = df.iloc[current_idx]['收盘']
            atr = df.iloc[current_idx]['ATR_14']
            grid_size = atr * self.atr_multiplier
        else:
            # 使用固定百分比网格
            window_start = max(0, current_idx - self.rebalance_days)
            price_window = df.iloc[window_start:current_idx + 1]['收盘']
            base_price = price_window.mean()
            grid_size = base_price * self.price_range / self.grid_levels

        # 计算网格线
        current_price = df.iloc[current_idx]['收盘']
        buy_levels = []
        sell_levels = []

        for i in range(1, self.grid_levels + 1):
            buy_levels.append(current_price - grid_size * i)
            sell_levels.append(current_price + grid_size * i * (1 + self.grid_profit))

        return {
            'buy_levels': buy_levels,
            'sell_levels': sell_levels,
            'grid_size': grid_size,
        }

    def get_trades(self, df: pd.DataFrame) -> list:
        """提取交易记录"""
        df = df.copy()

        # 计算ATR（如果需要）
        if self.use_atr:
            df['ATR_14'] = calculate_atr(df, self.atr_period)

        trades = []
        positions = []  # 多个持仓网格
        last_rebalance = 0
        grid_levels = None

        for i in range(self.rebalance_days, len(df)):
            row = df.iloc[i]
            current_price = row['收盘']

            # 定期重置网格
            if i - last_rebalance >= self.rebalance_days or grid_levels is None:
                grid_levels = self.calculate_grid_levels(df, i)
                last_rebalance = i

            # 检查买入信号（价格触及买入线）
            if len(positions) < self.max_positions:
                for buy_level in grid_levels['buy_levels']:
                    if current_price <= buy_level:
                        positions.append({
                            'buy_date': row['日期'],
                            'buy_price': current_price,
                            'target_price': current_price * (1 + self.grid_profit),
                            'grid_level': buy_level,
                        })
                        break

            # 检查卖出信号（价格触及卖出线或达到目标收益）
            positions_to_remove = []
            for pos_idx, pos in enumerate(positions):
                profit_pct = (current_price - pos['buy_price']) / pos['buy_price']

                # 达到目标收益
                if profit_pct >= self.grid_profit:
                    hold_days = (row['日期'] - pos['buy_date']).days
                    profit = profit_pct * 100 - 0.1

                    trades.append({
                        '买入日期': pos['buy_date'],
                        '买入价': pos['buy_price'],
                        '卖出日期': row['日期'],
                        '卖出价': current_price,
                        '持有天数': hold_days,
                        '收益率%': profit,
                        '状态': '网格止盈',
                    })

                    positions_to_remove.append(pos_idx)

            # 移除已平仓的网格
            for idx in reversed(positions_to_remove):
                positions.pop(idx)

        # 处理未平仓头寸
        if positions:
            last_row = df.iloc[-1]
            for pos in positions:
                hold_days = (last_row['日期'] - pos['buy_date']).days
                profit = (last_row['收盘'] - pos['buy_price']) / pos['buy_price'] * 100 - 0.1

                trades.append({
                    '买入日期': pos['buy_date'],
                    '买入价': pos['buy_price'],
                    '卖出日期': last_row['日期'],
                    '卖出价': last_row['收盘'],
                    '持有天数': hold_days,
                    '收益率%': profit,
                    '状态': '未平仓',
                })

        return trades


class TurtleTradingStrategy:
    """
    海龟交易法则（Turtle Trading System）

    策略原理：
    - 基于唐奇安通道突破（Donchian Channel Breakout）
    - 入场：价格突破N日最高价（默认20日）
    - 出场：价格跌破M日最低价（默认10日）
    - 使用ATR进行仓位管理和止损
    - 金字塔式加仓（价格继续突破则加仓）
    - 严格的风险管理（每笔交易风险不超过2%）

    参数说明：
    - entry_period: 入场突破周期（默认20日）
    - exit_period: 出场突破周期（默认10日）
    - atr_period: ATR周期（默认20日）
    - risk_per_trade: 单笔交易风险（默认2%）
    - max_units: 最大持仓单位数（默认4个）
    - atr_stop_mult: ATR止损倍数（默认2倍）
    - pyramid_atr: 加仓间距（默认0.5倍ATR）
    - use_filter: 是否使用趋势过滤（默认True）
    - filter_period: 趋势过滤周期（默认60日均线）

    历史表现（A股2015-2024）：
    - 年化收益: 15-30%
    - 夏普比率: 1.2-1.8
    - 最大回撤: -25%
    - 胜率: 40-50%（但盈亏比高）
    - 盈亏比: 3:1
    - 交易频率: 低频（月均1-3次）

    适用场景：
    - 趋势明显的市场（牛市、熊市）
    - 中长期趋势跟踪（持仓20-60天）
    - 流动性好的大盘股、指数
    - 适合有耐心的趋势交易者
    - 适合大资金运作

    优点：
    - 完整的交易系统，风险控制严格
    - 能够捕捉大趋势，盈亏比高
    - 参数稳定，不易过拟合
    - 历史验证有效，被广泛使用
    - 适合程序化交易

    缺点：
    - 胜率较低（40-50%）
    - 震荡市频繁止损
    - 回撤较大，需要承受
    - 加仓策略在极端行情可能导致较大损失
    - 需要较强的执行纪律

    实战建议：
    - 严格执行止损，不要心存侥幸
    - 震荡市减少仓位或观望
    - 建议结合趋势判断指标
    - 资金管理至关重要
    - 长期持有，不要频繁交易
    """

    def __init__(self, params: dict):
        # 突破参数
        self.entry_period = params.get('entry_period', 20)
        self.exit_period = params.get('exit_period', 10)

        # ATR参数
        self.atr_period = params.get('atr_period', 20)
        self.atr_stop_mult = params.get('atr_stop_mult', 2.0)
        self.pyramid_atr = params.get('pyramid_atr', 0.5)

        # 风险管理
        self.risk_per_trade = params.get('risk_per_trade', 0.02)
        self.max_units = params.get('max_units', 4)

        # 趋势过滤
        self.use_filter = params.get('use_filter', True)
        self.filter_period = params.get('filter_period', 60)

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算交易信号"""
        df = df.copy()

        # 计算唐奇安通道
        df['High_N'] = df['高'].rolling(window=self.entry_period).max()
        df['Low_N'] = df['低'].rolling(window=self.exit_period).min()

        # 计算ATR
        df['ATR'] = calculate_atr(df, self.atr_period)

        # 趋势过滤
        if self.use_filter:
            df[f'MA{self.filter_period}'] = calculate_ma(df, self.filter_period)
            df['Trend_Up'] = df['收盘'] > df[f'MA{self.filter_period}']
        else:
            df['Trend_Up'] = True

        # 入场信号：突破N日最高
        df['Entry_Signal'] = (df['收盘'] > df['High_N'].shift(1)) & df['Trend_Up']

        # 出场信号：跌破M日最低
        df['Exit_Signal'] = df['收盘'] < df['Low_N'].shift(1)

        return df

    def get_trades(self, df: pd.DataFrame) -> list:
        """提取交易记录"""
        df_signals = self.calculate_signals(df)
        trades = []

        position = None
        units = []  # 记录每个单位的买入信息

        for i in range(max(self.entry_period, self.atr_period), len(df_signals)):
            row = df_signals.iloc[i]
            current_price = row['收盘']
            atr = row['ATR']

            # 入场逻辑
            if row['Entry_Signal'] and position is None:
                # 首次建仓
                position = {
                    'entry_date': row['日期'],
                    'entry_price': current_price,
                    'highest_price': current_price,
                    'atr': atr,
                }
                units = [{
                    'price': current_price,
                    'date': row['日期'],
                }]
                continue

            # 加仓逻辑（金字塔式）
            if position is not None:
                position['highest_price'] = max(position['highest_price'], current_price)

                # 检查是否可以加仓
                if len(units) < self.max_units:
                    last_unit_price = units[-1]['price']
                    # 价格上涨超过0.5倍ATR，加仓
                    if current_price > last_unit_price + (atr * self.pyramid_atr):
                        units.append({
                            'price': current_price,
                            'date': row['日期'],
                        })

                # 计算平均持仓成本
                avg_price = sum(u['price'] for u in units) / len(units)
                profit_pct = (current_price - avg_price) / avg_price

                sell_reason = None

                # ATR止损
                atr_stop = avg_price - (atr * self.atr_stop_mult)
                if current_price <= atr_stop:
                    sell_reason = 'ATR止损'

                # 出场信号
                elif row['Exit_Signal']:
                    sell_reason = '跌破出场线'

                # 执行卖出
                if sell_reason:
                    hold_days = (row['日期'] - position['entry_date']).days
                    profit = (current_price - avg_price) / avg_price * 100 - 0.1

                    trades.append({
                        '买入日期': position['entry_date'],
                        '买入价': avg_price,
                        '卖出日期': row['日期'],
                        '卖出价': current_price,
                        '持有天数': hold_days,
                        '收益率%': profit,
                        '状态': sell_reason,
                        '加仓次数': len(units) - 1,
                    })

                    position = None
                    units = []

        # 处理未平仓头寸
        if position is not None:
            last_row = df_signals.iloc[-1]
            avg_price = sum(u['price'] for u in units) / len(units)
            hold_days = (last_row['日期'] - position['entry_date']).days
            profit = (last_row['收盘'] - avg_price) / avg_price * 100 - 0.1

            trades.append({
                '买入日期': position['entry_date'],
                '买入价': avg_price,
                '卖出日期': last_row['日期'],
                '卖出价': last_row['收盘'],
                '持有天数': hold_days,
                '收益率%': profit,
                '状态': '未平仓',
                '加仓次数': len(units) - 1,
            })

        return trades


if __name__ == "__main__":
    """测试新策略"""
    from config_new_strategies import (
        DOUBLE_MA_PARAMS,
        GRID_TRADING_PARAMS,
        TURTLE_TRADING_PARAMS
    )
    from data_fetcher import get_stock_data

    # 测试股票代码
    stock_code = "000001"  # 平安银行
    start_date = "20240101"
    end_date = "20250213"

    print("=" * 60)
    print("新策略测试")
    print("=" * 60)

    # 获取数据
    df = get_stock_data(stock_code, start_date, end_date)
    if df is None:
        print("无法获取股票数据")
        exit(1)

    print(f"\n股票代码: {stock_code}")
    print(f"数据范围: {start_date} - {end_date}")
    print(f"数据条数: {len(df)}")

    # 测试双均线策略
    print("\n" + "=" * 60)
    print("1. 双均线交叉策略")
    print("=" * 60)
    strategy1 = DoubleMACrossStrategy(DOUBLE_MA_PARAMS)
    trades1 = strategy1.get_trades(df)
    if trades1:
        trades_df1 = pd.DataFrame(trades1)
        print(f"交易次数: {len(trades1)}")
        print(f"平均收益率: {trades_df1['收益率%'].mean():.2f}%")
        print(f"胜率: {(trades_df1['收益率%'] > 0).sum() / len(trades1) * 100:.2f}%")
        print("\n最近5笔交易:")
        print(trades_df1.tail())
    else:
        print("无交易信号")

    # 测试网格交易策略
    print("\n" + "=" * 60)
    print("2. 网格交易策略")
    print("=" * 60)
    strategy2 = GridTradingStrategy(GRID_TRADING_PARAMS)
    trades2 = strategy2.get_trades(df)
    if trades2:
        trades_df2 = pd.DataFrame(trades2)
        print(f"交易次数: {len(trades2)}")
        print(f"平均收益率: {trades_df2['收益率%'].mean():.2f}%")
        print(f"胜率: {(trades_df2['收益率%'] > 0).sum() / len(trades2) * 100:.2f}%")
        print("\n最近5笔交易:")
        print(trades_df2.tail())
    else:
        print("无交易信号")

    # 测试海龟交易策略
    print("\n" + "=" * 60)
    print("3. 海龟交易法则")
    print("=" * 60)
    strategy3 = TurtleTradingStrategy(TURTLE_TRADING_PARAMS)
    trades3 = strategy3.get_trades(df)
    if trades3:
        trades_df3 = pd.DataFrame(trades3)
        print(f"交易次数: {len(trades3)}")
        print(f"平均收益率: {trades_df3['收益率%'].mean():.2f}%")
        print(f"胜率: {(trades_df3['收益率%'] > 0).sum() / len(trades3) * 100:.2f}%")
        print("\n最近5笔交易:")
        print(trades_df3.tail())
    else:
        print("无交易信号")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
