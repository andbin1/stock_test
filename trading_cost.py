"""
交易成本计算模块
包含手续费、印花税、滑点等完整交易成本
"""

from config import COMMISSION_RATE, STAMP_TAX, SLIPPAGE, TRADING_FEE_MIN


def calculate_trading_cost(buy_price: float, sell_price: float, shares: int = 100) -> dict:
    """
    计算完整的交易成本

    Args:
        buy_price: 买入价格
        sell_price: 卖出价格
        shares: 股数（默认100股，最小交易单位）

    Returns:
        dict: 包含各项成本和总成本的字典
    """
    # 买入金额
    buy_amount = buy_price * shares

    # 卖出金额
    sell_amount = sell_price * shares

    # 1. 买入手续费
    buy_commission = max(buy_amount * COMMISSION_RATE, TRADING_FEE_MIN)

    # 2. 买入滑点成本
    buy_slippage_cost = buy_amount * SLIPPAGE

    # 3. 卖出手续费
    sell_commission = max(sell_amount * COMMISSION_RATE, TRADING_FEE_MIN)

    # 4. 卖出印花税（仅卖出时收取）
    sell_stamp_tax = sell_amount * STAMP_TAX

    # 5. 卖出滑点成本
    sell_slippage_cost = sell_amount * SLIPPAGE

    # 总成本
    total_cost = (buy_commission + buy_slippage_cost +
                  sell_commission + sell_stamp_tax + sell_slippage_cost)

    # 成本占买入金额的百分比
    cost_pct = (total_cost / buy_amount) * 100 if buy_amount > 0 else 0

    return {
        'buy_commission': buy_commission,
        'buy_slippage': buy_slippage_cost,
        'sell_commission': sell_commission,
        'sell_stamp_tax': sell_stamp_tax,
        'sell_slippage': sell_slippage_cost,
        'total_cost': total_cost,
        'cost_pct': cost_pct,  # 总成本百分比
    }


def calculate_net_return(buy_price: float, sell_price: float, shares: int = 100) -> dict:
    """
    计算扣除交易成本后的净收益

    Args:
        buy_price: 买入价格
        sell_price: 卖出价格
        shares: 股数

    Returns:
        dict: 包含毛收益、交易成本、净收益的字典
    """
    # 毛收益
    gross_profit = (sell_price - buy_price) * shares
    gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100 if buy_price > 0 else 0

    # 交易成本
    cost_info = calculate_trading_cost(buy_price, sell_price, shares)

    # 净收益
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


def get_cost_summary() -> dict:
    """
    获取当前配置的交易成本摘要

    Returns:
        dict: 包含各项费率的字典
    """
    # 计算双边总成本率
    buy_cost_rate = COMMISSION_RATE + SLIPPAGE
    sell_cost_rate = COMMISSION_RATE + STAMP_TAX + SLIPPAGE
    total_cost_rate = buy_cost_rate + sell_cost_rate

    return {
        'commission_rate': COMMISSION_RATE,
        'commission_rate_pct': COMMISSION_RATE * 100,  # 转换为百分比显示
        'stamp_tax': STAMP_TAX,
        'stamp_tax_pct': STAMP_TAX * 100,
        'slippage': SLIPPAGE,
        'slippage_pct': SLIPPAGE * 100,
        'min_commission': TRADING_FEE_MIN,
        'total_cost_rate': total_cost_rate,
        'total_cost_rate_pct': total_cost_rate * 100,  # 双边总成本百分比
    }


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("交易成本计算示例")
    print("=" * 60)

    # 配置摘要
    summary = get_cost_summary()
    print("\n当前配置：")
    print(f"  手续费率：{summary['commission_rate_pct']:.3f}% (万{summary['commission_rate']*10000:.1f})")
    print(f"  印花税：{summary['stamp_tax_pct']:.3f}% (千{summary['stamp_tax']*1000:.0f})")
    print(f"  滑点：{summary['slippage_pct']:.3f}%")
    print(f"  最低手续费：{summary['min_commission']:.2f}元")
    print(f"  双边总成本：{summary['total_cost_rate_pct']:.3f}%")

    # 示例1：盈利交易
    print("\n" + "=" * 60)
    print("示例1：盈利交易（10元买入，11元卖出，100股）")
    print("=" * 60)

    result1 = calculate_net_return(10.0, 11.0, 100)
    print(f"毛收益：{result1['gross_profit']:.2f}元 ({result1['gross_profit_pct']:.2f}%)")
    print(f"交易成本：{result1['trading_cost']:.2f}元 ({result1['trading_cost_pct']:.2f}%)")
    print(f"  - 买入手续费：{result1['cost_breakdown']['buy_commission']:.2f}元")
    print(f"  - 买入滑点：{result1['cost_breakdown']['buy_slippage']:.2f}元")
    print(f"  - 卖出手续费：{result1['cost_breakdown']['sell_commission']:.2f}元")
    print(f"  - 卖出印花税：{result1['cost_breakdown']['sell_stamp_tax']:.2f}元")
    print(f"  - 卖出滑点：{result1['cost_breakdown']['sell_slippage']:.2f}元")
    print(f"净收益：{result1['net_profit']:.2f}元 ({result1['net_profit_pct']:.2f}%)")

    # 示例2：亏损交易
    print("\n" + "=" * 60)
    print("示例2：亏损交易（10元买入，9元卖出，100股）")
    print("=" * 60)

    result2 = calculate_net_return(10.0, 9.0, 100)
    print(f"毛收益：{result2['gross_profit']:.2f}元 ({result2['gross_profit_pct']:.2f}%)")
    print(f"交易成本：{result2['trading_cost']:.2f}元 ({result2['trading_cost_pct']:.2f}%)")
    print(f"净收益：{result2['net_profit']:.2f}元 ({result2['net_profit_pct']:.2f}%)")

    # 示例3：小额交易（触发最低手续费）
    print("\n" + "=" * 60)
    print("示例3：小额交易（5元买入，5.5元卖出，100股，触发最低手续费）")
    print("=" * 60)

    result3 = calculate_net_return(5.0, 5.5, 100)
    print(f"毛收益：{result3['gross_profit']:.2f}元 ({result3['gross_profit_pct']:.2f}%)")
    print(f"交易成本：{result3['trading_cost']:.2f}元 ({result3['trading_cost_pct']:.2f}%)")
    print(f"  - 买入手续费：{result3['cost_breakdown']['buy_commission']:.2f}元（触发最低{TRADING_FEE_MIN}元）")
    print(f"  - 卖出手续费：{result3['cost_breakdown']['sell_commission']:.2f}元（触发最低{TRADING_FEE_MIN}元）")
    print(f"净收益：{result3['net_profit']:.2f}元 ({result3['net_profit_pct']:.2f}%)")
