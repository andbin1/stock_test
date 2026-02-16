"""参数优化脚本 - 网格搜索找到最优参数"""
import pandas as pd
from itertools import product
from config import START_DATE, END_DATE, STRATEGY_PARAMS
from data_fetcher import get_batch_stock_data, get_index_constituents
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine


def optimize_parameters(stocks_data: dict, param_ranges: dict):
    """
    参数网格搜索优化

    示例:
    param_ranges = {
        "ma_period": [20, 30, 40],
        "volume_multiplier": [1.5, 2.0, 2.5],
        "hold_days": [2, 3, 4],
    }
    """
    print("🔍 开始参数优化...")

    # 生成所有参数组合
    keys = list(param_ranges.keys())
    values = list(param_ranges.values())
    param_combinations = []

    for combo in product(*values):
        param_dict = dict(zip(keys, combo))
        # 保留原有参数
        full_params = STRATEGY_PARAMS.copy()
        full_params.update(param_dict)
        param_combinations.append(full_params)

    print(f"   共{len(param_combinations)}个参数组合待测试\n")

    results_list = []
    engine = BacktestEngine()

    for idx, params in enumerate(param_combinations, 1):
        print(f"[{idx}/{len(param_combinations)}] 测试参数: {params}")

        # 创建策略
        strategy = VolumeBreakoutStrategy(params)

        # 运行回测
        backtest_results = engine.run_multiple_stocks(stocks_data, strategy)
        aggregated = BacktestEngine.aggregate_results(backtest_results)

        # 记录结果
        result = {
            'ma_period': params.get('ma_period', STRATEGY_PARAMS['ma_period']),
            'volume_multiplier': params.get('volume_multiplier', STRATEGY_PARAMS['volume_multiplier']),
            'hold_days': params.get('hold_days', STRATEGY_PARAMS['hold_days']),
            'trades': aggregated['total_trades'],
            'total_return': aggregated['total_return'],
            'avg_return': aggregated['avg_return_per_trade'],
            'win_rate': aggregated['win_rate'],
            'profit_factor': aggregated['profit_factor'],
        }
        results_list.append(result)
        print(f"   结果: 交易数={result['trades']}, 总收益={result['total_return']:.2f}%, 胜率={result['win_rate']:.1f}%\n")

    # 转换为DataFrame并排序
    results_df = pd.DataFrame(results_list)

    # 按多个指标排序
    results_df = results_df.sort_values(
        by=['total_return', 'win_rate', 'profit_factor'],
        ascending=[False, False, False]
    )

    print("\n" + "=" * 100)
    print("✅ 优化完成！最优参数排名：")
    print("=" * 100)
    print(results_df.head(10).to_string(index=False))

    # 保存结果
    results_df.to_csv('参数优化结果.csv', index=False, encoding='utf-8-sig')
    print("\n✓ 详细结果已保存到: 参数优化结果.csv")

    return results_df


if __name__ == "__main__":
    print("=" * 60)
    print("  A股交易策略 - 参数优化")
    print("=" * 60)

    # 获取数据（仅沪深300，加速测试）
    print("\n获取数据中...")
    stocks = get_index_constituents("000300", limit=30)
    stocks_data = get_batch_stock_data(stocks, START_DATE, END_DATE)

    if not stocks_data:
        print("❌ 获取数据失败")
        exit(1)

    # 定义参数搜索范围
    param_ranges = {
        "ma_period": [20, 30, 40],
        "volume_multiplier": [1.5, 2.0, 2.5],
        "hold_days": [2, 3, 4],
    }

    # 运行优化
    results = optimize_parameters(stocks_data, param_ranges)

    # 推荐最优参数
    best_params = results.iloc[0]
    print("\n💡 推荐参数组合:")
    print(f"   ma_period: {int(best_params['ma_period'])}")
    print(f"   volume_multiplier: {best_params['volume_multiplier']}")
    print(f"   hold_days: {int(best_params['hold_days'])}")
    print(f"\n   预期收益: {best_params['total_return']:.2f}%")
    print(f"   预期胜率: {best_params['win_rate']:.1f}%")
