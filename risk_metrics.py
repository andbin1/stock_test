"""
风险指标计算模块
计算回测结果的各项风险指标（最大回撤、年化收益、夏普比率等）
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Optional


class RiskMetricsCalculator:
    """
    风险指标计算器

    使用矢量化计算方式计算各项风险指标，支持单股和多股聚合计算。
    """

    def __init__(self,
                 trades_data: Union[List[Dict], pd.DataFrame],
                 initial_capital: float = 100000,
                 trading_days_per_year: int = 252,
                 risk_free_rate: float = 0.02):
        """
        初始化风险指标计算器

        Args:
            trades_data: 交易记录列表或DataFrame，包含'收益率%'列
            initial_capital: 初始资本（元）
            trading_days_per_year: 年交易天数（默认252天）
            risk_free_rate: 无风险利率（默认2%）
        """
        # 将交易数据转换为DataFrame
        if isinstance(trades_data, list):
            self.trades_df = pd.DataFrame(trades_data)
        else:
            self.trades_df = trades_data.copy()

        self.initial_capital = initial_capital
        self.trading_days_per_year = trading_days_per_year
        self.risk_free_rate = risk_free_rate

        # 提取收益率数据
        if '收益率%' in self.trades_df.columns:
            self.returns = self.trades_df['收益率%'].values / 100  # 转换为小数
        else:
            self.returns = np.array([])

        self.num_trades = len(self.returns)

    def _calculate_cumulative_returns(self) -> np.ndarray:
        """
        计算累积收益

        Returns:
            numpy数组，包含每次交易后的累积收益率
        """
        if len(self.returns) == 0:
            return np.array([])

        # 从初始资本开始，逐次计算账户价值
        capital_values = np.cumprod(1 + self.returns) * self.initial_capital
        cumulative_returns = (capital_values - self.initial_capital) / self.initial_capital

        return cumulative_returns

    def max_drawdown(self) -> float:
        """
        计算最大回撤（最大跌幅）

        最大回撤 = (峰值 - 谷值) / 峰值

        Returns:
            float: 最大回撤率（范围0-1），例如0.15表示15%
        """
        if len(self.returns) == 0:
            return 0.0

        cumulative = self._calculate_cumulative_returns()

        if len(cumulative) == 0:
            return 0.0

        # 计算运行最大值（从开始到当前的最大累积收益）
        running_max = np.maximum.accumulate(cumulative)

        # 计算回撤：当前值相对于运行最大值的下降
        drawdown = (cumulative - running_max) / (1 + running_max)

        # 返回最大回撤的绝对值
        max_dd = np.min(drawdown)

        return abs(max_dd)

    def annual_return(self) -> float:
        """
        计算年化收益率

        假设一年有trading_days_per_year个交易日

        Returns:
            float: 年化收益率（范围0-1），例如0.20表示20%
        """
        if len(self.returns) == 0:
            return 0.0

        # 总收益率
        total_return = np.prod(1 + self.returns) - 1

        # 年化：(1 + 总收益)^(年交易日/实际交易日) - 1
        num_years = self.num_trades / self.trading_days_per_year

        if num_years <= 0:
            return 0.0

        annual_ret = (1 + total_return) ** (1 / num_years) - 1

        return max(annual_ret, 0.0)  # 确保不返回负值

    def annual_volatility(self) -> float:
        """
        计算年化波动率（标准差）

        将日交易收益率的标准差年化

        Returns:
            float: 年化波动率（范围0-1），例如0.20表示20%
        """
        if len(self.returns) < 2:
            return 0.0

        # 计算交易收益率的标准差
        daily_std = np.std(self.returns, ddof=1)  # 使用样本标准差

        # 年化：daily_std * sqrt(交易天数)
        annual_vol = daily_std * np.sqrt(self.trading_days_per_year)

        return annual_vol

    def sharpe_ratio(self) -> float:
        """
        计算夏普比率

        夏普比率 = (年化收益 - 无风险利率) / 年化波动率

        更高的夏普比率表示风险调整后收益更好

        Returns:
            float: 夏普比率，例如1.5表示单位风险承受1.5倍收益
        """
        annual_vol = self.annual_volatility()

        # 避免除以零
        if annual_vol == 0:
            return 0.0

        annual_ret = self.annual_return()
        sharpe = (annual_ret - self.risk_free_rate) / annual_vol

        return sharpe

    def calmar_ratio(self) -> float:
        """
        计算卡玛比率

        卡玛比率 = 年化收益 / 最大回撤

        更高的卡玛比率表示相对最大回撤的收益更好

        Returns:
            float: 卡玛比率，例如2.0表示年化收益是最大回撤的2倍
        """
        max_dd = self.max_drawdown()

        # 避免除以零
        if max_dd == 0:
            return 0.0

        annual_ret = self.annual_return()
        calmar = annual_ret / max_dd

        return calmar

    def sortino_ratio(self) -> float:
        """
        计算索提诺比率

        类似夏普比率，但只考虑下行波动率（负收益的波动）

        索提诺比率 = (年化收益 - 无风险利率) / 下行波动率

        Returns:
            float: 索提诺比率
        """
        # 只计算负收益的波动率
        negative_returns = self.returns[self.returns < 0]

        if len(negative_returns) < 2:
            # 如果没有负收益或只有1个，返回高分
            annual_ret = self.annual_return()
            return annual_ret / 0.01 if annual_ret > 0 else 0.0

        # 下行波动率
        downside_std = np.std(negative_returns, ddof=1)
        downside_vol = downside_std * np.sqrt(self.trading_days_per_year)

        if downside_vol == 0:
            return 0.0

        annual_ret = self.annual_return()
        sortino = (annual_ret - self.risk_free_rate) / downside_vol

        return sortino

    def profit_factor(self) -> float:
        """
        计算盈亏比

        盈亏比 = 平均盈利 / 平均亏损

        Returns:
            float: 盈亏比，例如2.0表示平均盈利是亏损的2倍
        """
        if len(self.returns) == 0:
            return 0.0

        # 分离收益和亏损
        profits = self.returns[self.returns > 0]
        losses = np.abs(self.returns[self.returns < 0])

        avg_profit = np.mean(profits) if len(profits) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0

        # 避免除以零
        if avg_loss == 0:
            return 0.0 if avg_profit == 0 else float('inf')

        return avg_profit / avg_loss

    def win_rate(self) -> float:
        """
        计算胜率

        胜率 = 盈利交易数 / 总交易数

        Returns:
            float: 胜率（范围0-1），例如0.55表示55%
        """
        if self.num_trades == 0:
            return 0.0

        winning_trades = np.sum(self.returns > 0)

        return winning_trades / self.num_trades

    def max_single_loss(self) -> float:
        """
        计算单笔最大亏损

        Returns:
            float: 最大单笔亏损率（范围0-1），例如0.10表示10%
        """
        if len(self.returns) == 0:
            return 0.0

        min_return = np.min(self.returns)

        # 返回负收益的绝对值
        return abs(min_return) if min_return < 0 else 0.0

    def all_metrics(self) -> Dict[str, float]:
        """
        计算并返回所有风险指标

        Returns:
            dict: 包含所有风险指标的字典
        """
        metrics = {
            'num_trades': self.num_trades,
            'total_return': float(np.prod(1 + self.returns) - 1) if len(self.returns) > 0 else 0.0,
            'annual_return': self.annual_return(),
            'annual_volatility': self.annual_volatility(),
            'sharpe_ratio': self.sharpe_ratio(),
            'calmar_ratio': self.calmar_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'max_drawdown': self.max_drawdown(),
            'profit_factor': self.profit_factor(),
            'win_rate': self.win_rate(),
            'max_single_loss': self.max_single_loss(),
        }

        return metrics


def aggregate_risk_metrics(all_trades: List[Dict]) -> Dict[str, float]:
    """
    聚合多个交易结果计算风险指标

    用于多股回测结果的聚合计算

    Args:
        all_trades: 所有交易记录的列表

    Returns:
        dict: 聚合后的风险指标
    """
    if not all_trades:
        return {
            'num_trades': 0,
            'annual_return': 0.0,
            'annual_volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
        }

    calculator = RiskMetricsCalculator(all_trades)
    return calculator.all_metrics()


if __name__ == "__main__":
    # 测试示例
    print("=" * 70)
    print("风险指标计算示例")
    print("=" * 70)

    # 创建样例交易数据
    sample_trades = [
        {'收益率%': 1.5},
        {'收益率%': -0.8},
        {'收益率%': 2.3},
        {'收益率%': 0.5},
        {'收益率%': -1.2},
        {'收益率%': 3.1},
        {'收益率%': -0.3},
        {'收益率%': 1.8},
        {'收益率%': 2.5},
        {'收益率%': -0.9},
    ]

    # 计算风险指标
    calculator = RiskMetricsCalculator(sample_trades, initial_capital=100000)
    metrics = calculator.all_metrics()

    print(f"\n总交易数: {metrics['num_trades']}")
    print(f"总收益: {metrics['total_return']:.2%}")
    print(f"年化收益: {metrics['annual_return']:.2%}")
    print(f"年化波动率: {metrics['annual_volatility']:.2%}")
    print(f"最大回撤: {metrics['max_drawdown']:.2%}")
    print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"卡玛比率: {metrics['calmar_ratio']:.2f}")
    print(f"索提诺比率: {metrics['sortino_ratio']:.2f}")
    print(f"盈亏比: {metrics['profit_factor']:.2f}")
    print(f"胜率: {metrics['win_rate']:.2%}")
    print(f"最大单笔亏损: {metrics['max_single_loss']:.2%}")
