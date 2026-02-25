"""回测引擎 - 执行回测并计算绩效指标"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from trading_cost import get_cost_summary


class BacktestEngine:
    """
    回测引擎 - 支持交易成本计算

    功能：
    1. 计算持仓数量（按手取整）
    2. 应用滑点到买卖价格
    3. 计算交易手续费
    4. 聚合回测统计结果
    """

    def __init__(self, initial_capital: float = None, position_ratio: float = None,
                 commission_rate: float = None, slippage: float = None):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金（元），默认100000
            position_ratio: 单笔交易占比（0-1），默认0.2
            commission_rate: 手续费率（0-1），默认0.001
            slippage: 滑点（0-1），默认0.0
        """
        from config import (
            INITIAL_CAPITAL_DEFAULT, POSITION_RATIO_DEFAULT,
            COMMISSION_RATE_DEFAULT, SLIPPAGE_DEFAULT
        )

        self.initial_capital = initial_capital or INITIAL_CAPITAL_DEFAULT
        self.position_ratio = position_ratio or POSITION_RATIO_DEFAULT
        self.commission_rate = commission_rate or COMMISSION_RATE_DEFAULT
        self.slippage = slippage or SLIPPAGE_DEFAULT

        # 记录回测设置（用于结果返回）
        self.backtest_settings = {
            'initial_capital': self.initial_capital,
            'position_ratio': self.position_ratio,
            'commission_rate': self.commission_rate,
            'slippage': self.slippage,
        }

    def calculate_position_size(self, price: float) -> int:
        """
        根据当前价格计算持仓数量

        公式: position_size = floor(initial_capital * position_ratio / price)
        按手(100股)取整

        Args:
            price: 当前股票价格

        Returns:
            持仓数量（已按手取整）
        """
        if price <= 0:
            return 0
        amount = self.initial_capital * self.position_ratio / price
        return int(amount // 100) * 100  # 按手计算

    def apply_slippage_to_price(self, price: float, is_buy: bool) -> float:
        """
        应用滑点到价格

        买入价 = 原价 * (1 + 滑点)
        卖出价 = 原价 * (1 - 滑点)

        Args:
            price: 原始价格
            is_buy: 是否为买入（True为买入，False为卖出）

        Returns:
            应用滑点后的价格
        """
        if is_buy:
            return price * (1 + self.slippage)
        else:
            return price * (1 - self.slippage)

    def calculate_trade_cost(self, amount: float) -> float:
        """
        计算交易成本（手续费）

        成本 = 交易金额 * 手续费率

        Args:
            amount: 交易金额

        Returns:
            交易成本（手续费）
        """
        return amount * self.commission_rate

    def apply_trading_costs(self, trade: dict) -> dict:
        """
        对单笔交易应用成本计算

        流程：
        1. 应用滑点到买入价和卖出价
        2. 计算正确的持仓数量
        3. 计算买卖成本（手续费）
        4. 重新计算收益率

        Args:
            trade: 原始交易记录字典

        Returns:
            更新后的交易记录（包含成本信息）
        """
        trade_copy = trade.copy()

        # 1. 应用滑点
        buy_price_with_slip = self.apply_slippage_to_price(trade_copy['买入价'], is_buy=True)
        sell_price_with_slip = self.apply_slippage_to_price(trade_copy['卖出价'], is_buy=False)

        # 2. 计算持仓数量
        position_size = self.calculate_position_size(buy_price_with_slip)

        # 3. 计算交易金额和成本
        buy_amount = buy_price_with_slip * position_size
        sell_amount = sell_price_with_slip * position_size
        buy_cost = self.calculate_trade_cost(buy_amount)
        sell_cost = self.calculate_trade_cost(sell_amount)

        # 4. 重新计算收益率
        total_cost = buy_amount + buy_cost + sell_cost
        profit = sell_amount - buy_amount - buy_cost - sell_cost
        return_rate = (profit / total_cost) * 100 if total_cost > 0 else 0

        # 5. 保存到交易记录
        trade_copy['买入价'] = buy_price_with_slip
        trade_copy['卖出价'] = sell_price_with_slip
        trade_copy['持仓数量'] = position_size
        trade_copy['买入成本'] = round(buy_cost, 2)
        trade_copy['卖出成本'] = round(sell_cost, 2)
        trade_copy['收益率%'] = return_rate

        return trade_copy

    def run_single_stock(self, symbol: str, df: pd.DataFrame, strategy: Any) -> dict:
        """
        对单只股票运行回测

        流程：
        1. 获取策略生成的交易信号
        2. 对每笔交易应用成本计算（滑点、手续费）
        3. 计算回测统计指标
        """
        trades = strategy.get_trades(df)

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

        # 盈亏比
        avg_profit = trades_df[trades_df['收益率%'] > 0]['收益率%'].mean() if wins > 0 else 0
        avg_loss = abs(trades_df[trades_df['收益率%'] <= 0]['收益率%'].mean()) if losses > 0 else 0
        profit_factor = avg_profit / avg_loss if avg_loss > 0 else (1 if avg_profit > 0 else 0)

        # 最大单笔亏损
        max_loss = trades_df['收益率%'].min() if len(trades_df) > 0 else 0

        return {
            'symbol': symbol,
            'trades': trades_with_costs,
            'total_return': total_return,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_return': trades_df['收益率%'].mean(),
            'max_loss': max_loss,
            'profit_factor': profit_factor,
            'trades_df': trades_df,
            'backtest_settings': self.backtest_settings,
        }

    def run_multiple_stocks(self, stocks_data: Dict[str, pd.DataFrame],
                           strategy: Any) -> Dict[str, dict]:
        """对多只股票运行回测"""
        results = {}

        for symbol, df in stocks_data.items():
            if df is None or len(df) < 50:  # 数据不足跳过
                continue

            result = self.run_single_stock(symbol, df, strategy)
            if result['num_trades'] > 0:  # 只记录有交易的
                results[symbol] = result

        return results

    @staticmethod
    def aggregate_results(results: Dict[str, dict]) -> dict:
        """聚合所有股票的回测结果"""
        if not results:
            return {
                'total_trades': 0,
                'total_return': 0,
                'stocks_count': 0,
                'avg_return_per_trade': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
            }

        all_returns = []
        all_trades = 0
        total_wins = 0
        total_losses = 0

        for symbol, result in results.items():
            if 'trades_df' in result:
                all_returns.extend(result['trades_df']['收益率%'].tolist())
                all_trades += result['num_trades']
                total_wins += len(result['trades_df'][result['trades_df']['收益率%'] > 0])
                total_losses += len(result['trades_df'][result['trades_df']['收益率%'] <= 0])

        if not all_returns:
            return {
                'total_trades': 0,
                'total_return': 0,
                'stocks_count': 0,
                'avg_return_per_trade': 0,
                'win_rate': 0,
            }

        all_returns = np.array(all_returns)
        wins = all_returns[all_returns > 0]
        losses = all_returns[all_returns <= 0]

        return {
            'stocks_count': len(results),
            'total_trades': all_trades,
            'total_return': all_returns.sum(),
            'avg_return_per_trade': all_returns.mean(),
            'max_single_return': all_returns.max(),
            'min_single_return': all_returns.min(),
            'win_rate': (total_wins / all_trades * 100) if all_trades > 0 else 0,
            'avg_profit': wins.mean() if len(wins) > 0 else 0,
            'avg_loss': abs(losses.mean()) if len(losses) > 0 else 0,
            'profit_factor': (wins.mean() / abs(losses.mean())) if len(losses) > 0 and losses.mean() != 0 else 0,
        }


if __name__ == "__main__":
    from config import STRATEGY_PARAMS
    from data_fetcher import get_stock_data

    df = get_stock_data("000001", "20240101", "20250213")
    if df is not None:
        strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
        engine = BacktestEngine()
        result = engine.run_single_stock("000001", df, strategy)

        print("=== 回测结果 ===")
        print(f"总交易数: {result['num_trades']}")
        print(f"总收益: {result['total_return']:.2f}%")
        print(f"平均收益: {result['avg_return']:.2f}%")
        print(f"胜率: {result['win_rate']:.2f}%")
        print(f"盈亏比: {result['profit_factor']:.2f}")
        print(f"最大单笔亏损: {result['max_loss']:.2f}%")
