"""回测引擎 - 执行回测并计算绩效指标"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from trading_cost import get_cost_summary


class BacktestEngine:
    """
    简化的回测引擎

    注意：交易成本（手续费、印花税、滑点）由策略在计算收益率时已扣除，
    本引擎主要负责聚合统计结果。
    """

    def __init__(self, initial_capital: float = 100000, commission_rate: float = None):
        self.initial_capital = initial_capital
        # commission_rate保留用于兼容，但实际使用config.py中的配置
        if commission_rate is not None:
            self.commission_rate = commission_rate
        else:
            cost_summary = get_cost_summary()
            self.commission_rate = cost_summary['commission_rate']

    def run_single_stock(self, symbol: str, df: pd.DataFrame, strategy: Any) -> dict:
        """对单只股票运行回测"""
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
            }

        trades_df = pd.DataFrame(trades)

        # 计算收益统计
        total_return = trades_df['收益率%'].sum()
        num_trades = len(trades)
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
            'trades': trades,
            'total_return': total_return,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_return': trades_df['收益率%'].mean(),
            'max_loss': max_loss,
            'profit_factor': profit_factor,
            'trades_df': trades_df,
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
