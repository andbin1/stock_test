"""
交易成本计算模块 V2
支持单笔交易、批量交易、以及完整的成本分析
采用矢量化计算提升性能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Tuple, Optional
from config import COMMISSION_RATE, STAMP_TAX, SLIPPAGE, TRADING_FEE_MIN


class TradingCostCalculator:
    """
    交易成本计算器

    支持单笔、批量、矢量化计算交易成本，包括手续费、印花税、滑点等。
    """

    def __init__(self,
                 commission_rate: float = COMMISSION_RATE,
                 stamp_tax: float = STAMP_TAX,
                 slippage: float = SLIPPAGE,
                 min_commission: float = TRADING_FEE_MIN):
        """
        初始化交易成本计算器

        Args:
            commission_rate: 手续费率（默认万2.5 = 0.00025）
            stamp_tax: 印花税率（默认千1 = 0.001，仅卖出）
            slippage: 滑点率（默认0.1% = 0.001）
            min_commission: 最低手续费（默认5元，单边）
        """
        self.commission_rate = commission_rate
        self.stamp_tax = stamp_tax
        self.slippage = slippage
        self.min_commission = min_commission

    def calculate_trading_cost(self,
                              buy_price: float,
                              sell_price: float,
                              shares: int = 100) -> Dict[str, float]:
        """
        计算单笔交易的完整成本

        成本包括：
        1. 买入手续费 = max(买入金额 × 手续费率, 最低手续费)
        2. 买入滑点 = 买入金额 × 滑点率
        3. 卖出手续费 = max(卖出金额 × 手续费率, 最低手续费)
        4. 卖出印花税 = 卖出金额 × 印花税率（仅卖出）
        5. 卖出滑点 = 卖出金额 × 滑点率

        Args:
            buy_price: 买入价格（元）
            sell_price: 卖出价格（元）
            shares: 股数（默认100股，最小交易单位）

        Returns:
            dict: 包含各项成本明细和总成本的字典
        """
        if buy_price <= 0 or shares <= 0:
            return {
                'buy_commission': 0.0,
                'buy_slippage': 0.0,
                'sell_commission': 0.0,
                'sell_stamp_tax': 0.0,
                'sell_slippage': 0.0,
                'total_cost': 0.0,
                'cost_pct': 0.0,
            }

        # 买入和卖出金额
        buy_amount = buy_price * shares
        sell_amount = sell_price * shares

        # 买入成本
        buy_commission = max(buy_amount * self.commission_rate, self.min_commission)
        buy_slippage = buy_amount * self.slippage

        # 卖出成本
        sell_commission = max(sell_amount * self.commission_rate, self.min_commission)
        sell_stamp_tax = sell_amount * self.stamp_tax
        sell_slippage = sell_amount * self.slippage

        # 总成本
        total_cost = buy_commission + buy_slippage + sell_commission + sell_stamp_tax + sell_slippage

        # 成本占买入金额的百分比
        cost_pct = (total_cost / buy_amount) * 100 if buy_amount > 0 else 0

        return {
            'buy_commission': buy_commission,
            'buy_slippage': buy_slippage,
            'sell_commission': sell_commission,
            'sell_stamp_tax': sell_stamp_tax,
            'sell_slippage': sell_slippage,
            'total_cost': total_cost,
            'cost_pct': cost_pct,
        }

    def calculate_net_return(self,
                            buy_price: float,
                            sell_price: float,
                            shares: int = 100) -> Dict[str, float]:
        """
        计算扣除交易成本后的净收益

        Args:
            buy_price: 买入价格（元）
            sell_price: 卖出价格（元）
            shares: 股数（默认100股）

        Returns:
            dict: 包含毛收益、交易成本、净收益及各项百分比的字典
        """
        if buy_price <= 0 or shares <= 0:
            return {
                'gross_profit': 0.0,
                'gross_profit_pct': 0.0,
                'trading_cost': 0.0,
                'trading_cost_pct': 0.0,
                'net_profit': 0.0,
                'net_profit_pct': 0.0,
                'cost_breakdown': {},
            }

        # 毛收益（未扣成本）
        gross_profit = (sell_price - buy_price) * shares
        gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100 if buy_price > 0 else 0

        # 交易成本
        cost_info = self.calculate_trading_cost(buy_price, sell_price, shares)

        # 净收益 = 毛收益 - 交易成本
        net_profit = gross_profit - cost_info['total_cost']
        net_profit_pct = (net_profit / (buy_price * shares)) * 100 if buy_price * shares > 0 else 0

        return {
            'gross_profit': gross_profit,
            'gross_profit_pct': gross_profit_pct,
            'trading_cost': cost_info['total_cost'],
            'trading_cost_pct': cost_info['cost_pct'],
            'net_profit': net_profit,
            'net_profit_pct': net_profit_pct,
            'cost_breakdown': cost_info,
        }

    def batch_calculate_net_return(self,
                                   buy_prices: Union[List[float], np.ndarray],
                                   sell_prices: Union[List[float], np.ndarray],
                                   shares: Union[int, List[int], np.ndarray] = 100) -> Dict[str, np.ndarray]:
        """
        批量计算多笔交易的净收益（矢量化计算）

        Args:
            buy_prices: 买入价格数组
            sell_prices: 卖出价格数组
            shares: 股数（可以是单一值或数组）

        Returns:
            dict: 包含各项指标的numpy数组
        """
        # 转换为numpy数组
        buy_prices = np.array(buy_prices)
        sell_prices = np.array(sell_prices)

        if isinstance(shares, (int, float)):
            shares = np.full_like(buy_prices, shares, dtype=float)
        else:
            shares = np.array(shares)

        # 买入和卖出金额
        buy_amounts = buy_prices * shares
        sell_amounts = sell_prices * shares

        # 避免除以零 - 使用np.where处理
        safe_buy_prices = np.where(buy_prices > 0, buy_prices, 1)
        safe_buy_amounts = np.where(buy_amounts > 0, buy_amounts, 1)

        # 买入成本（需要处理最低手续费）
        commission_pct = buy_amounts * self.commission_rate
        buy_commission = np.maximum(commission_pct, self.min_commission)
        buy_slippage = buy_amounts * self.slippage

        # 卖出成本
        commission_pct_sell = sell_amounts * self.commission_rate
        sell_commission = np.maximum(commission_pct_sell, self.min_commission)
        sell_stamp_tax = sell_amounts * self.stamp_tax
        sell_slippage = sell_amounts * self.slippage

        # 总成本
        total_cost = buy_commission + buy_slippage + sell_commission + sell_stamp_tax + sell_slippage

        # 毛收益和净收益
        gross_profit = (sell_prices - buy_prices) * shares
        gross_profit_pct = ((sell_prices - buy_prices) / safe_buy_prices) * 100

        net_profit = gross_profit - total_cost
        net_profit_pct = (net_profit / safe_buy_amounts) * 100

        return {
            'buy_commission': buy_commission,
            'buy_slippage': buy_slippage,
            'sell_commission': sell_commission,
            'sell_stamp_tax': sell_stamp_tax,
            'sell_slippage': sell_slippage,
            'total_cost': total_cost,
            'cost_pct': (total_cost / safe_buy_amounts) * 100,
            'gross_profit': gross_profit,
            'gross_profit_pct': gross_profit_pct,
            'net_profit': net_profit,
            'net_profit_pct': net_profit_pct,
        }

    def get_cost_summary(self) -> Dict[str, float]:
        """
        获取当前配置的交易成本摘要

        Returns:
            dict: 包含各项费率和总成本的字典
        """
        # 单边成本率
        buy_cost_rate = self.commission_rate + self.slippage
        sell_cost_rate = self.commission_rate + self.stamp_tax + self.slippage
        total_cost_rate = buy_cost_rate + sell_cost_rate

        return {
            'commission_rate': self.commission_rate,
            'commission_rate_pct': self.commission_rate * 100,
            'commission_rate_bps': self.commission_rate * 10000,  # 基点表示
            'stamp_tax': self.stamp_tax,
            'stamp_tax_pct': self.stamp_tax * 100,
            'slippage': self.slippage,
            'slippage_pct': self.slippage * 100,
            'min_commission': self.min_commission,
            'buy_cost_rate': buy_cost_rate,
            'buy_cost_rate_pct': buy_cost_rate * 100,
            'sell_cost_rate': sell_cost_rate,
            'sell_cost_rate_pct': sell_cost_rate * 100,
            'total_cost_rate': total_cost_rate,
            'total_cost_rate_pct': total_cost_rate * 100,
        }


def batch_apply_cost(returns_pct: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
    """
    对收益率数组批量扣除交易成本

    这是一个简化版本，直接从收益率中扣除近似成本

    Args:
        returns_pct: 交易收益率数组（百分比）

    Returns:
        array: 扣除成本后的收益率数组
    """
    returns = np.array(returns_pct)

    # 双边总成本（百分点）
    total_cost_pct = (COMMISSION_RATE + SLIPPAGE) * 100 + (COMMISSION_RATE + STAMP_TAX + SLIPPAGE) * 100

    # 从收益率中扣除总成本
    net_returns = returns - total_cost_pct

    return net_returns


if __name__ == "__main__":
    # 测试示例
    print("=" * 70)
    print("交易成本计算模块 V2 - 测试示例")
    print("=" * 70)

    # 初始化计算器
    calc = TradingCostCalculator()

    # 成本摘要
    summary = calc.get_cost_summary()
    print("\n当前配置摘要：")
    print(f"  手续费率：{summary['commission_rate_pct']:.3f}% (万{summary['commission_rate_bps']:.1f})")
    print(f"  印花税：{summary['stamp_tax_pct']:.3f}%")
    print(f"  滑点：{summary['slippage_pct']:.3f}%")
    print(f"  最低手续费：{summary['min_commission']:.2f}元")
    print(f"  买方成本：{summary['buy_cost_rate_pct']:.3f}%")
    print(f"  卖方成本：{summary['sell_cost_rate_pct']:.3f}%")
    print(f"  双边总成本：{summary['total_cost_rate_pct']:.3f}%")

    # 示例1：盈利交易
    print("\n" + "=" * 70)
    print("示例1：盈利交易（买入10元，卖出11元，100股）")
    print("=" * 70)

    result1 = calc.calculate_net_return(10.0, 11.0, 100)
    print(f"毛收益：{result1['gross_profit']:.2f}元 ({result1['gross_profit_pct']:.2f}%)")
    print(f"交易成本：{result1['trading_cost']:.2f}元 ({result1['trading_cost_pct']:.2f}%)")
    print(f"  - 买入手续费：{result1['cost_breakdown']['buy_commission']:.2f}元")
    print(f"  - 买入滑点：{result1['cost_breakdown']['buy_slippage']:.2f}元")
    print(f"  - 卖出手续费：{result1['cost_breakdown']['sell_commission']:.2f}元")
    print(f"  - 卖出印花税：{result1['cost_breakdown']['sell_stamp_tax']:.2f}元")
    print(f"  - 卖出滑点：{result1['cost_breakdown']['sell_slippage']:.2f}元")
    print(f"净收益：{result1['net_profit']:.2f}元 ({result1['net_profit_pct']:.2f}%)")

    # 示例2：亏损交易
    print("\n" + "=" * 70)
    print("示例2：亏损交易（买入10元，卖出9元，100股）")
    print("=" * 70)

    result2 = calc.calculate_net_return(10.0, 9.0, 100)
    print(f"毛收益：{result2['gross_profit']:.2f}元 ({result2['gross_profit_pct']:.2f}%)")
    print(f"交易成本：{result2['trading_cost']:.2f}元 ({result2['trading_cost_pct']:.2f}%)")
    print(f"净收益：{result2['net_profit']:.2f}元 ({result2['net_profit_pct']:.2f}%)")

    # 示例3：批量计算
    print("\n" + "=" * 70)
    print("示例3：批量计算（5笔交易）")
    print("=" * 70)

    buy_prices = [10, 20, 15, 12, 8]
    sell_prices = [11, 19, 16, 11, 8.5]
    batch_result = calc.batch_calculate_net_return(buy_prices, sell_prices)

    for i in range(len(buy_prices)):
        print(f"交易{i+1}：买{buy_prices[i]:.1f}卖{sell_prices[i]:.1f} "
              f"净收益{batch_result['net_profit_pct'][i]:.2f}%")

    print(f"\n批量交易总净收益：{batch_result['net_profit_pct'].sum():.2f}%")
