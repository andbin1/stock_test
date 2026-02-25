"""
增强版回测引擎 - 实现专业的仓位管理和时间范围控制
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


class PortfolioManager:
    """投资组合仓位管理 - 实现资金管理和风险控制"""

    def __init__(self, initial_capital: float, max_position_ratio: float = 0.80):
        """
        初始化投资组合管理器

        Args:
            initial_capital: 初始资金（元）
            max_position_ratio: 最大持仓比例（默认80%）
        """
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.max_position_ratio = max_position_ratio
        self.positions = {}  # {symbol: {'shares': 100, 'entry_price': 10, 'entry_cost': 1000, ...}}
        self.trade_history = []
        self.rejected_trades = []  # 被风险控制阻止的交易

    def get_total_position_value(self) -> float:
        """获取当前持仓总成本"""
        total = sum(pos['entry_cost'] for pos in self.positions.values())
        return total

    def get_position_ratio(self) -> float:
        """获取当前仓位比例 (持仓值 / 初始资金)"""
        total_value = self.get_total_position_value()
        return total_value / self.initial_capital

    def can_enter_position(self, symbol: str, entry_cost: float) -> tuple[bool, str]:
        """
        检查是否可以建仓

        Returns:
            (can_enter: bool, reason: str)
        """
        current_ratio = self.get_position_ratio()
        potential_ratio = (self.get_total_position_value() + entry_cost) / self.initial_capital

        # 检查是否会超过最大仓位限制
        if potential_ratio > self.max_position_ratio:
            return False, f"仓位将超过{self.max_position_ratio*100:.0f}%限制"

        # 检查是否有足够现金
        if entry_cost > self.current_cash:
            return False, f"现金不足(需要{entry_cost:.0f}, 有{self.current_cash:.0f})"

        return True, "可以建仓"

    def buy(self, symbol: str, shares: int, entry_price: float,
            entry_cost: float, buy_date: str) -> bool:
        """
        买入股票

        Returns:
            成功返回True，失败返回False
        """
        total_cost = shares * entry_price + entry_cost

        can_buy, reason = self.can_enter_position(symbol, total_cost)
        if not can_buy:
            self.rejected_trades.append({
                'date': buy_date,
                'symbol': symbol,
                'action': 'BUY',
                'reason': reason,
                'amount': total_cost,
                'current_ratio': self.get_position_ratio()
            })
            return False

        self.positions[symbol] = {
            'shares': shares,
            'entry_price': entry_price,
            'entry_cost': total_cost,
            'buy_date': buy_date,
            'status': 'open'
        }
        self.current_cash -= total_cost

        self.trade_history.append({
            'date': buy_date,
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': entry_price,
            'commission': entry_cost,
            'total_cost': total_cost,
            'cash_after': self.current_cash,
            'position_ratio': self.get_position_ratio()
        })

        return True

    def sell(self, symbol: str, shares: int, exit_price: float,
             exit_cost: float, sell_date: str) -> bool:
        """
        卖出股票

        Returns:
            成功返回True，失败返回False
        """
        if symbol not in self.positions:
            return False

        position = self.positions[symbol]
        sell_income = shares * exit_price - exit_cost

        self.current_cash += sell_income

        # 计算收益
        entry_cost = position['entry_cost']
        profit = sell_income - (entry_cost * shares / position['shares'])
        profit_pct = (profit / entry_cost) * 100 if entry_cost > 0 else 0

        del self.positions[symbol]

        self.trade_history.append({
            'date': sell_date,
            'symbol': symbol,
            'action': 'SELL',
            'shares': shares,
            'price': exit_price,
            'commission': exit_cost,
            'income': sell_income,
            'profit': profit,
            'profit_pct': profit_pct,
            'cash_after': self.current_cash,
            'position_ratio': self.get_position_ratio()
        })

        return True

    def get_report(self) -> dict:
        """获取投资组合最终报告"""
        final_value = self.current_cash + self.get_total_position_value()
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100

        return {
            'initial_capital': self.initial_capital,
            'final_cash': round(self.current_cash, 2),
            'final_position_value': round(self.get_total_position_value(), 2),
            'final_total_value': round(final_value, 2),
            'total_return_pct': round(total_return, 2),
            'final_position_ratio': round(self.get_position_ratio() * 100, 2),
            'num_trades': len(self.trade_history),
            'num_rejected': len(self.rejected_trades),
            'active_positions': list(self.positions.keys()),
            'trade_history': self.trade_history,
            'rejected_trades': self.rejected_trades
        }


class TradingCostCalculator:
    """A股真实交易成本计算"""

    def __init__(self, commission_rate: float = 0.0001, include_stamp_duty: bool = True):
        """
        Args:
            commission_rate: 手续费率 (0.01%-0.03%, 默认0.01%)
            include_stamp_duty: 是否计入印花税 (卖出时0.1%)
        """
        self.commission_rate = commission_rate
        self.stamp_duty_sell = 0.001 if include_stamp_duty else 0  # 印花税 (卖出 0.1%)
        self.transfer_fee_rate = 0.000001  # 过户费

    def calculate_buy_cost(self, amount: float) -> float:
        """计算买入成本"""
        commission = amount * self.commission_rate
        transfer_fee = amount * self.transfer_fee_rate
        return commission + transfer_fee

    def calculate_sell_cost(self, amount: float) -> float:
        """计算卖出成本"""
        commission = amount * self.commission_rate
        stamp_duty = amount * self.stamp_duty_sell
        transfer_fee = amount * self.transfer_fee_rate
        return commission + stamp_duty + transfer_fee

    def get_total_cost_ratio(self) -> float:
        """获取单个往返的总成本比例"""
        buy_cost = self.calculate_buy_cost(100)
        sell_cost = self.calculate_sell_cost(100)
        total = (buy_cost + sell_cost) / 100
        return total


class BacktestTimeConfig:
    """回测时间配置 - 分离数据范围和回测范围"""

    def __init__(self, data_start: str = None, data_end: str = None,
                 backtest_start: str = None, backtest_end: str = None):
        """
        Args:
            data_start: 数据下载开始日期 (格式: 'YYYY-MM-DD')
            data_end: 数据下载结束日期
            backtest_start: 回测开始日期 (独立设置)
            backtest_end: 回测结束日期 (独立设置)
        """
        self.data_start = data_start or "2024-01-01"
        self.data_end = data_end or "2025-02-24"
        self.backtest_start = backtest_start or "2024-06-01"
        self.backtest_end = backtest_end or "2025-01-31"

        # 验证时间范围
        self._validate_ranges()

    def _validate_ranges(self):
        """验证时间范围的合理性"""
        data_start = pd.to_datetime(self.data_start)
        data_end = pd.to_datetime(self.data_end)
        backtest_start = pd.to_datetime(self.backtest_start)
        backtest_end = pd.to_datetime(self.backtest_end)

        assert data_start < data_end, "数据开始日期必须早于结束日期"
        assert backtest_start < backtest_end, "回测开始日期必须早于结束日期"
        assert data_start <= backtest_start, "数据范围必须包含回测范围"
        assert backtest_end <= data_end, "数据范围必须包含回测范围"

    def get_warmup_period(self) -> int:
        """获取预热期天数 (数据开始到回测开始之间)"""
        data_start = pd.to_datetime(self.data_start)
        backtest_start = pd.to_datetime(self.backtest_start)
        return (backtest_start - data_start).days

    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """按回测时间范围过滤数据"""
        df = df.copy()
        df['日期'] = pd.to_datetime(df['日期'])

        mask = (df['日期'] >= self.backtest_start) & (df['日期'] <= self.backtest_end)
        return df[mask].reset_index(drop=True)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'data_start': self.data_start,
            'data_end': self.data_end,
            'backtest_start': self.backtest_start,
            'backtest_end': self.backtest_end,
            'warmup_days': self.get_warmup_period()
        }


class EnhancedBacktestEngine:
    """增强版回测引擎 - 支持时间范围和仓位管理"""

    def __init__(self, initial_capital: float = None, position_ratio: float = None,
                 commission_rate: float = None, slippage: float = None,
                 time_config: BacktestTimeConfig = None,
                 max_position_ratio: float = 0.80):
        """
        初始化增强版回测引擎

        Args:
            initial_capital: 初始资金（元），默认100000
            position_ratio: 单笔交易占比（0-1），默认0.2
            commission_rate: 手续费率（0-1），默认0.001
            slippage: 滑点（0-1），默认0.0
            time_config: 回测时间配置
            max_position_ratio: 最大仓位比例（默认0.80 = 80%）
        """
        from config import (
            INITIAL_CAPITAL_DEFAULT, POSITION_RATIO_DEFAULT,
            COMMISSION_RATE_DEFAULT, SLIPPAGE_DEFAULT
        )

        self.initial_capital = initial_capital or INITIAL_CAPITAL_DEFAULT
        self.position_ratio = position_ratio or POSITION_RATIO_DEFAULT
        self.commission_rate = commission_rate or COMMISSION_RATE_DEFAULT
        self.slippage = slippage or SLIPPAGE_DEFAULT
        self.max_position_ratio = max_position_ratio

        # 时间配置
        self.time_config = time_config or BacktestTimeConfig()

        # 成本计算器
        self.cost_calculator = TradingCostCalculator(self.commission_rate)

        # 记录回测设置
        self.backtest_settings = {
            'initial_capital': self.initial_capital,
            'position_ratio': self.position_ratio,
            'commission_rate': self.commission_rate,
            'slippage': self.slippage,
            'max_position_ratio': self.max_position_ratio,
            'time_config': self.time_config.to_dict()
        }

    def calculate_position_size(self, price: float) -> int:
        """根据当前价格计算持仓数量"""
        if price <= 0:
            return 0
        amount = self.initial_capital * self.position_ratio / price
        return int(amount // 100) * 100  # 按手计算

    def apply_slippage_to_price(self, price: float, is_buy: bool) -> float:
        """应用滑点到价格"""
        if is_buy:
            return price * (1 + self.slippage)
        else:
            return price * (1 - self.slippage)

    def apply_trading_costs(self, trade: dict) -> dict:
        """对单笔交易应用成本计算 - 使用真实成本"""
        trade_copy = trade.copy()

        buy_price_with_slip = self.apply_slippage_to_price(trade_copy['买入价'], is_buy=True)
        sell_price_with_slip = self.apply_slippage_to_price(trade_copy['卖出价'], is_buy=False)

        position_size = self.calculate_position_size(buy_price_with_slip)

        buy_amount = buy_price_with_slip * position_size
        sell_amount = sell_price_with_slip * position_size

        # 使用真实的成本结构
        buy_cost = self.cost_calculator.calculate_buy_cost(buy_amount)
        sell_cost = self.cost_calculator.calculate_sell_cost(sell_amount)
        stamp_duty = sell_amount * 0.001  # 印花税

        total_cost = buy_amount + buy_cost + sell_cost
        profit = sell_amount - buy_amount - buy_cost - sell_cost
        return_rate = (profit / total_cost) * 100 if total_cost > 0 else 0

        trade_copy['买入价'] = round(buy_price_with_slip, 2)
        trade_copy['卖出价'] = round(sell_price_with_slip, 2)
        trade_copy['持仓数量'] = position_size
        trade_copy['买入成本'] = round(buy_cost, 2)
        trade_copy['卖出成本'] = round(sell_cost, 2)
        trade_copy['印花税'] = round(stamp_duty, 2)
        trade_copy['总手续费'] = round(buy_cost + sell_cost, 2)
        trade_copy['收益率%'] = round(return_rate, 2)

        return trade_copy

    def run_single_stock(self, symbol: str, df: pd.DataFrame, strategy: Any) -> dict:
        """对单只股票运行回测（带时间过滤）"""
        # 按时间范围过滤数据
        df_backtest = self.time_config.filter_data(df)

        if len(df_backtest) == 0:
            return {
                'symbol': symbol,
                'trades': [],
                'total_return': 0,
                'num_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'max_loss': 0,
                'profit_factor': 0,
                'backtest_settings': self.backtest_settings,
                'backtest_period': {
                    'start': self.time_config.backtest_start,
                    'end': self.time_config.backtest_end,
                    'data_points': 0
                }
            }

        trades = strategy.get_trades(df_backtest)

        if not trades:
            return {
                'symbol': symbol,
                'trades': [],
                'total_return': 0,
                'num_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'max_loss': 0,
                'profit_factor': 0,
                'backtest_settings': self.backtest_settings,
                'backtest_period': {
                    'start': self.time_config.backtest_start,
                    'end': self.time_config.backtest_end,
                    'data_points': len(df_backtest)
                }
            }

        # 应用成本计算到每笔交易
        trades_with_costs = [self.apply_trading_costs(trade) for trade in trades]

        trades_df = pd.DataFrame(trades_with_costs)

        # 计算收益统计
        total_return = trades_df['收益率%'].sum()
        num_trades = len(trades_with_costs)
        wins = len(trades_df[trades_df['收益率%'] > 0])
        losses = len(trades_df[trades_df['收益率%'] <= 0])
        win_rate = wins / num_trades * 100 if num_trades > 0 else 0

        avg_profit = trades_df[trades_df['收益率%'] > 0]['收益率%'].mean() if wins > 0 else 0
        avg_loss = abs(trades_df[trades_df['收益率%'] <= 0]['收益率%'].mean()) if losses > 0 else 0
        profit_factor = avg_profit / avg_loss if avg_loss > 0 else (1 if avg_profit > 0 else 0)

        max_loss = trades_df['收益率%'].min() if len(trades_df) > 0 else 0

        return {
            'symbol': symbol,
            'trades': trades_with_costs,
            'total_return': round(total_return, 2),
            'num_trades': num_trades,
            'win_rate': round(win_rate, 2),
            'avg_return': round(trades_df['收益率%'].mean(), 2),
            'max_loss': round(max_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'trades_df': trades_df,
            'backtest_settings': self.backtest_settings,
            'backtest_period': {
                'start': self.time_config.backtest_start,
                'end': self.time_config.backtest_end,
                'data_points': len(df_backtest),
                'warmup_days': self.time_config.get_warmup_period()
            }
        }

    def run_multiple_stocks_with_portfolio(self, all_data: dict, strategy: Any) -> dict:
        """
        多只股票回测 - 带真实的投资组合管理

        Returns:
            包含投资组合总结和每只股票详细结果
        """
        pm = PortfolioManager(
            initial_capital=self.initial_capital,
            max_position_ratio=self.max_position_ratio
        )

        results = {}
        stock_results = {}

        for symbol, df in all_data.items():
            df_backtest = self.time_config.filter_data(df)
            if len(df_backtest) == 0:
                continue

            trades = strategy.get_trades(df_backtest)

            for trade in trades:
                # 处理买入
                if '买入日期' in trade and '卖出日期' in trade:
                    buy_price_with_slip = self.apply_slippage_to_price(trade['买入价'], is_buy=True)
                    position_size = self.calculate_position_size(buy_price_with_slip)
                    buy_amount = buy_price_with_slip * position_size
                    buy_cost = self.cost_calculator.calculate_buy_cost(buy_amount)

                    # 检查是否可以建仓
                    buy_accepted = pm.buy(
                        symbol=symbol,
                        shares=position_size,
                        entry_price=buy_price_with_slip,
                        entry_cost=buy_cost,
                        buy_date=trade['买入日期']
                    )

                    if not buy_accepted:
                        trade['portfolio_status'] = 'REJECTED'
                        trade['rejection_reason'] = f"仓位超限或现金不足"
                        continue

                    trade['portfolio_status'] = 'ACCEPTED'

                    # 处理卖出
                    if trade.get('状态') == '平仓':
                        sell_price_with_slip = self.apply_slippage_to_price(trade['卖出价'], is_buy=False)
                        sell_amount = sell_price_with_slip * position_size
                        sell_cost = self.cost_calculator.calculate_sell_cost(sell_amount)

                        pm.sell(
                            symbol=symbol,
                            shares=position_size,
                            exit_price=sell_price_with_slip,
                            exit_cost=sell_cost,
                            sell_date=trade['卖出日期']
                        )

            # 存储每只股票的结果
            stock_results[symbol] = {
                'trades': trades,
                'num_trades': len(trades)
            }

        # 生成投资组合总结
        pm_report = pm.get_report()

        results['portfolio_summary'] = {
            'initial_capital': pm_report['initial_capital'],
            'final_cash': pm_report['final_cash'],
            'final_position_value': pm_report['final_position_value'],
            'final_total_value': pm_report['final_total_value'],
            'total_return_pct': pm_report['total_return_pct'],
            'final_position_ratio': pm_report['final_position_ratio'],
            'num_trades_executed': pm_report['num_trades'],
            'num_trades_rejected': pm_report['num_rejected'],
            'active_positions': pm_report['active_positions'],
            'backtest_period': {
                'start': self.time_config.backtest_start,
                'end': self.time_config.backtest_end,
                'warmup_days': self.time_config.get_warmup_period()
            }
        }

        results['stock_results'] = stock_results
        results['trade_history'] = pm_report['trade_history']
        results['rejected_trades'] = pm_report['rejected_trades']

        return results

    def run_multiple_stocks(self, all_data: dict, strategy: Any) -> dict:
        """向后兼容的多股票回测方法"""
        return self.run_multiple_stocks_with_portfolio(all_data, strategy)
