"""
回测引擎 V2
完整的回测框架，集成成本计算和风险指标
支持单股、多股回测及完整的性能分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from risk_metrics import RiskMetricsCalculator, aggregate_risk_metrics
from trading_cost_v2 import TradingCostCalculator


class BacktestEngineV2:
    """
    完整的回测引擎 V2

    功能：
    1. 执行单股和多股回测
    2. 计算完整的风险指标
    3. 聚合多股结果
    4. 详细的性能分析和报告
    """

    def __init__(self,
                 initial_capital: float = 100000,
                 trading_days_per_year: int = 252,
                 risk_free_rate: float = 0.02,
                 commission_rate: float = None,
                 stamp_tax: float = None,
                 slippage: float = None,
                 min_commission: float = None):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资本（元），默认10万
            trading_days_per_year: 年交易天数，默认252天
            risk_free_rate: 无风险利率，默认2%
            commission_rate: 手续费率（为None时使用默认值）
            stamp_tax: 印花税率（为None时使用默认值）
            slippage: 滑点率（为None时使用默认值）
            min_commission: 最低手续费（为None时使用默认值）
        """
        self.initial_capital = initial_capital
        self.trading_days_per_year = trading_days_per_year
        self.risk_free_rate = risk_free_rate

        # 初始化交易成本计算器
        kwargs = {}
        if commission_rate is not None:
            kwargs['commission_rate'] = commission_rate
        if stamp_tax is not None:
            kwargs['stamp_tax'] = stamp_tax
        if slippage is not None:
            kwargs['slippage'] = slippage
        if min_commission is not None:
            kwargs['min_commission'] = min_commission

        self.cost_calculator = TradingCostCalculator(**kwargs)

    def run_single_stock(self,
                        symbol: str,
                        df: pd.DataFrame,
                        strategy: Any) -> Dict[str, Any]:
        """
        对单只股票执行回测

        Args:
            symbol: 股票代码
            df: 股票行情数据（包含OHLCV等）
            strategy: 交易策略对象（需要有get_trades()方法）

        Returns:
            dict: 包含交易记录、收益统计、风险指标的完整回测结果
        """
        # 获取交易信号
        trades = strategy.get_trades(df)

        # 如果没有交易，返回空结果
        if not trades:
            return {
                'symbol': symbol,
                'trades': [],
                'trades_count': 0,
                'metrics': self._empty_metrics(),
                'cost_summary': self.cost_calculator.get_cost_summary(),
            }

        # 转换为DataFrame便于计算
        trades_df = pd.DataFrame(trades)

        # 确保有收益率列
        if '收益率%' not in trades_df.columns:
            return {
                'symbol': symbol,
                'trades': trades,
                'trades_count': len(trades),
                'metrics': self._empty_metrics(),
                'cost_summary': self.cost_calculator.get_cost_summary(),
            }

        # 计算风险指标
        calculator = RiskMetricsCalculator(
            trades_df,
            initial_capital=self.initial_capital,
            trading_days_per_year=self.trading_days_per_year,
            risk_free_rate=self.risk_free_rate
        )
        metrics = calculator.all_metrics()

        return {
            'symbol': symbol,
            'trades': trades,
            'trades_df': trades_df,
            'trades_count': len(trades),
            'metrics': metrics,
            'cost_summary': self.cost_calculator.get_cost_summary(),
        }

    def run_multiple_stocks(self,
                          stocks_data: Dict[str, pd.DataFrame],
                          strategy: Any,
                          min_data_points: int = 50) -> Dict[str, Dict[str, Any]]:
        """
        对多只股票执行回测

        Args:
            stocks_data: 股票数据字典，格式为 {symbol: df, ...}
            strategy: 交易策略对象
            min_data_points: 最少数据点数（低于此值跳过该股票）

        Returns:
            dict: 每只股票的回测结果字典
        """
        results = {}

        for symbol, df in stocks_data.items():
            # 检查数据有效性
            if df is None or len(df) < min_data_points:
                continue

            try:
                result = self.run_single_stock(symbol, df, strategy)

                # 只记录有交易的股票
                if result['trades_count'] > 0:
                    results[symbol] = result
            except Exception as e:
                print(f"警告: 股票{symbol}回测失败: {str(e)}")
                continue

        return results

    def aggregate_results(self,
                         results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        聚合多只股票的回测结果

        Args:
            results: 单股回测结果字典

        Returns:
            dict: 聚合后的统计指标和风险指标
        """
        if not results:
            return self._empty_aggregated_metrics()

        # 收集所有交易
        all_trades = []
        all_trades_dfs = []

        for symbol, result in results.items():
            if 'trades_df' in result:
                all_trades_dfs.append(result['trades_df'])
                all_trades.extend(result['trades'])

        if not all_trades:
            return self._empty_aggregated_metrics()

        # 合并所有交易的DataFrame
        combined_trades_df = pd.concat(all_trades_dfs, ignore_index=True)

        # 计算聚合的风险指标
        calculator = RiskMetricsCalculator(
            combined_trades_df,
            initial_capital=self.initial_capital,
            trading_days_per_year=self.trading_days_per_year,
            risk_free_rate=self.risk_free_rate
        )
        risk_metrics = calculator.all_metrics()

        # 基础统计
        returns_array = combined_trades_df['收益率%'].values

        aggregated = {
            'stocks_count': len(results),
            'total_trades': len(all_trades),
            'total_return': float(np.sum(returns_array)),
            'avg_return_per_trade': float(np.mean(returns_array)),
            'median_return_per_trade': float(np.median(returns_array)),
            'max_single_return': float(np.max(returns_array)),
            'min_single_return': float(np.min(returns_array)),
            'std_return': float(np.std(returns_array)),
            'risk_metrics': risk_metrics,
            'cost_summary': self.cost_calculator.get_cost_summary(),
        }

        return aggregated

    def _empty_metrics(self) -> Dict[str, float]:
        """返回空的风险指标对象"""
        return {
            'num_trades': 0,
            'total_return': 0.0,
            'annual_return': 0.0,
            'annual_volatility': 0.0,
            'sharpe_ratio': 0.0,
            'calmar_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': 0.0,
            'profit_factor': 0.0,
            'win_rate': 0.0,
            'max_single_loss': 0.0,
        }

    def _empty_aggregated_metrics(self) -> Dict[str, Any]:
        """返回空的聚合指标对象"""
        return {
            'stocks_count': 0,
            'total_trades': 0,
            'total_return': 0.0,
            'avg_return_per_trade': 0.0,
            'median_return_per_trade': 0.0,
            'max_single_return': 0.0,
            'min_single_return': 0.0,
            'std_return': 0.0,
            'risk_metrics': self._empty_metrics(),
            'cost_summary': self.cost_calculator.get_cost_summary(),
        }

    def generate_report(self, result: Dict[str, Any], is_single: bool = True) -> str:
        """
        生成回测报告

        Args:
            result: 回测结果字典
            is_single: 是否为单股报告

        Returns:
            str: 格式化的报告文本
        """
        report = []

        if is_single:
            report.append("=" * 70)
            report.append(f"单股回测报告: {result['symbol']}")
            report.append("=" * 70)
            report.append(f"\n交易统计:")
            report.append(f"  总交易数: {result['trades_count']}")

            if result['metrics']:
                metrics = result['metrics']
                report.append(f"\n收益指标:")
                report.append(f"  总收益: {metrics['total_return']:.2%}")
                report.append(f"  平均单笔收益: {metrics['total_return']/max(metrics['num_trades'],1):.2%}")
                report.append(f"  年化收益: {metrics['annual_return']:.2%}")

                report.append(f"\n风险指标:")
                report.append(f"  年化波动率: {metrics['annual_volatility']:.2%}")
                report.append(f"  最大回撤: {metrics['max_drawdown']:.2%}")
                report.append(f"  胜率: {metrics['win_rate']:.2%}")
                report.append(f"  盈亏比: {metrics['profit_factor']:.2f}")

                report.append(f"\n风险调整收益:")
                report.append(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
                report.append(f"  卡玛比率: {metrics['calmar_ratio']:.2f}")
                report.append(f"  索提诺比率: {metrics['sortino_ratio']:.2f}")

        else:
            report.append("=" * 70)
            report.append("多股回测聚合报告")
            report.append("=" * 70)
            report.append(f"\n概览:")
            report.append(f"  参与回测股票数: {result['stocks_count']}")
            report.append(f"  总交易数: {result['total_trades']}")

            report.append(f"\n收益统计:")
            report.append(f"  总收益: {result['total_return']:.2%}")
            report.append(f"  平均单笔收益: {result['avg_return_per_trade']:.2%}")
            report.append(f"  中位数收益: {result['median_return_per_trade']:.2%}")

            report.append(f"\n收益波动:")
            report.append(f"  最大收益: {result['max_single_return']:.2%}")
            report.append(f"  最小收益: {result['min_single_return']:.2%}")
            report.append(f"  标准差: {result['std_return']:.2%}")

            if result['risk_metrics']:
                metrics = result['risk_metrics']
                report.append(f"\n风险指标:")
                report.append(f"  年化收益: {metrics['annual_return']:.2%}")
                report.append(f"  年化波动率: {metrics['annual_volatility']:.2%}")
                report.append(f"  最大回撤: {metrics['max_drawdown']:.2%}")
                report.append(f"  胜率: {metrics['win_rate']:.2%}")
                report.append(f"  盈亏比: {metrics['profit_factor']:.2f}")

                report.append(f"\n风险调整收益:")
                report.append(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
                report.append(f"  卡玛比率: {metrics['calmar_ratio']:.2f}")
                report.append(f"  索提诺比率: {metrics['sortino_ratio']:.2f}")

        return "\n".join(report)


if __name__ == "__main__":
    # 测试示例
    print("=" * 70)
    print("回测引擎 V2 - 测试示例")
    print("=" * 70)

    # 初始化引擎
    engine = BacktestEngineV2(initial_capital=100000)

    # 创建样例交易数据
    sample_trades = [
        {'symbol': '000001', '收益率%': 1.5, 'entry_date': '2024-01-01'},
        {'symbol': '000001', '收益率%': -0.8, 'entry_date': '2024-01-02'},
        {'symbol': '000001', '收益率%': 2.3, 'entry_date': '2024-01-03'},
        {'symbol': '000001', '收益率%': 0.5, 'entry_date': '2024-01-04'},
        {'symbol': '000001', '收益率%': -1.2, 'entry_date': '2024-01-05'},
    ]

    trades_df = pd.DataFrame(sample_trades)

    print("\n样例交易数据：")
    print(trades_df)

    # 计算风险指标
    calculator = RiskMetricsCalculator(trades_df)
    metrics = calculator.all_metrics()

    print("\n风险指标：")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # 成本摘要
    cost_summary = engine.cost_calculator.get_cost_summary()
    print("\n交易成本摘要：")
    print(f"  双边总成本: {cost_summary['total_cost_rate_pct']:.3f}%")
