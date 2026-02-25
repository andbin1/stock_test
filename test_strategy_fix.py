"""测试策略修复"""
import pandas as pd
from data_fetcher import get_stock_data
from strategy import VolumeBreakoutStrategy
from strategy_fixed import VolumeBreakoutStrategyFixed
from config import STRATEGY_PARAMS

# 获取数据
symbol = "000001"
df = get_stock_data(symbol, "20240101", "20250131")

if df is not None:
    print("="*80)
    print("【原始版本 vs 修复版本对比】")
    print("="*80)

    # 测试不同的hold_days
    for hold_days in [1, 3, 5]:
        print(f"\n【hold_days={hold_days}】")
        print("-"*80)

        params = STRATEGY_PARAMS.copy()
        params['hold_days'] = hold_days

        # 原始版本
        strategy_old = VolumeBreakoutStrategy(params)
        trades_old = strategy_old.get_trades(df)

        # 修复版本
        strategy_new = VolumeBreakoutStrategyFixed(params)
        trades_new = strategy_new.get_trades(df)

        df_old = pd.DataFrame(trades_old)
        df_new = pd.DataFrame(trades_new)

        print(f"原始版本:")
        print(f"  交易数: {len(trades_old)}")
        if trades_old:
            print(f"  平均收益率: {df_old['收益率%'].mean():.4f}%")
            print(f"  最小收益率: {df_old['收益率%'].min():.4f}%")
            print(f"  最大收益率: {df_old['收益率%'].max():.4f}%")
            # 检查同一天买卖的数量
            df_old['日期匹配'] = df_old['买入日期'] == df_old['卖出日期']
            same_day_count = df_old['日期匹配'].sum()
            print(f"  同一天买卖数: {same_day_count} ⚠️" if same_day_count > 0 else f"  同一天买卖数: {same_day_count}")

        print(f"\n修复版本:")
        print(f"  交易数: {len(trades_new)}")
        if trades_new:
            print(f"  平均收益率: {df_new['收益率%'].mean():.4f}%")
            print(f"  最小收益率: {df_new['收益率%'].min():.4f}%")
            print(f"  最大收益率: {df_new['收益率%'].max():.4f}%")
            # 检查同一天买卖的数量
            df_new['日期匹配'] = df_new['买入日期'] == df_new['卖出日期']
            same_day_count = df_new['日期匹配'].sum()
            print(f"  同一天买卖数: {same_day_count}")

        if trades_old and trades_new:
            print(f"\n收益率差异: {abs(df_old['收益率%'].mean() - df_new['收益率%'].mean()):.4f}%")
            print(f"交易数差异: {len(trades_old) - len(trades_new)}")

        # 打印前5笔交易对比
        print(f"\n【前3笔交易对比】")
        print(f"原始版本:")
        for idx, trade in enumerate(trades_old[:3]):
            buy_date = trade['买入日期'].strftime('%Y-%m-%d')
            sell_date = trade['卖出日期'].strftime('%Y-%m-%d')
            marker = " ⚠️ 同一天" if buy_date == sell_date else ""
            print(f"  {idx+1}. {buy_date} ({trade['买入价']:.2f}元) -> {sell_date} ({trade['卖出价']:.2f}元) "
                  f"持有{trade['持有天数']}天 收益{trade['收益率%']:.4f}%{marker}")

        print(f"\n修复版本:")
        for idx, trade in enumerate(trades_new[:3]):
            buy_date = trade['买入日期'].strftime('%Y-%m-%d')
            sell_date = trade['卖出日期'].strftime('%Y-%m-%d')
            print(f"  {idx+1}. {buy_date} ({trade['买入价']:.2f}元) -> {sell_date} ({trade['卖出价']:.2f}元) "
                  f"持有{trade['持有天数']}天 收益{trade['收益率%']:.4f}%")
