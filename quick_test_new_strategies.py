"""
快速测试新策略
用于验证策略是否能正常运行
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入新策略
from strategy_new import (
    DoubleMACrossStrategy,
    GridTradingStrategy,
    TurtleTradingStrategy
)

# 导入配置
from config_new_strategies import (
    DOUBLE_MA_PARAMS,
    GRID_TRADING_PARAMS,
    TURTLE_TRADING_PARAMS
)


def generate_mock_data(days=250):
    """生成模拟股票数据（用于测试）"""
    np.random.seed(42)

    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # 生成价格数据（带趋势和随机波动）
    trend = np.linspace(10, 15, days)
    noise = np.random.normal(0, 0.5, days)
    close_prices = trend + noise

    # 生成其他数据
    high_prices = close_prices + np.random.uniform(0, 0.5, days)
    low_prices = close_prices - np.random.uniform(0, 0.5, days)
    open_prices = close_prices + np.random.normal(0, 0.2, days)
    volumes = np.random.uniform(1000000, 5000000, days)
    amounts = volumes * close_prices

    df = pd.DataFrame({
        '日期': dates,
        '开盘': open_prices,
        '收盘': close_prices,
        '高': high_prices,
        '低': low_prices,
        '成交量': volumes,
        '成交额': amounts,
    })

    return df


def test_strategy(strategy_name, strategy_class, params, df):
    """测试单个策略"""
    print(f"\n{'=' * 60}")
    print(f"测试策略：{strategy_name}")
    print(f"{'=' * 60}")

    try:
        # 创建策略实例
        strategy = strategy_class(params)
        print("✅ 策略实例创建成功")

        # 生成交易信号
        trades = strategy.get_trades(df)
        print(f"✅ 交易信号生成成功，共 {len(trades)} 笔交易")

        if trades:
            trades_df = pd.DataFrame(trades)

            # 基本统计
            avg_return = trades_df['收益率%'].mean()
            win_rate = (trades_df['收益率%'] > 0).sum() / len(trades) * 100
            avg_hold_days = trades_df['持有天数'].mean()

            print(f"\n交易统计：")
            print(f"  交易次数：{len(trades)}")
            print(f"  平均收益率：{avg_return:.2f}%")
            print(f"  胜率：{win_rate:.2f}%")
            print(f"  平均持仓天数：{avg_hold_days:.1f}天")

            # 显示前3笔交易
            print(f"\n前3笔交易：")
            print(trades_df.head(3)[['买入日期', '买入价', '卖出日期', '卖出价', '收益率%', '状态']].to_string(index=False))

            return True
        else:
            print("⚠️  无交易信号（可能数据不足或条件未满足）")
            return True

    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("新策略快速测试")
    print("=" * 60)
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 生成模拟数据
    print(f"\n生成模拟数据（250天）...")
    df = generate_mock_data(days=250)
    print(f"✅ 数据生成成功，共 {len(df)} 条记录")
    print(f"   价格范围：{df['收盘'].min():.2f} - {df['收盘'].max():.2f}")
    print(f"   日期范围：{df['日期'].min().date()} - {df['日期'].max().date()}")

    # 测试所有策略
    strategies = [
        ("双均线交叉策略", DoubleMACrossStrategy, DOUBLE_MA_PARAMS),
        ("网格交易策略", GridTradingStrategy, GRID_TRADING_PARAMS),
        ("海龟交易法则", TurtleTradingStrategy, TURTLE_TRADING_PARAMS),
    ]

    results = []
    for strategy_name, strategy_class, params in strategies:
        success = test_strategy(strategy_name, strategy_class, params, df)
        results.append((strategy_name, success))

    # 测试总结
    print(f"\n{'=' * 60}")
    print("测试总结")
    print(f"{'=' * 60}")

    for strategy_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {strategy_name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print(f"\n🎉 所有策略测试通过！")
        print(f"\n后续步骤：")
        print(f"  1. 运行 python demo_new_strategies.py 查看完整演示")
        print(f"  2. 使用真实数据进行回测")
        print(f"  3. 根据回测结果调整参数")
    else:
        print(f"\n⚠️  部分策略测试失败，请检查代码")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
