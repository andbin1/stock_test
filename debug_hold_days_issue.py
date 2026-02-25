"""诊断持股天数bug"""
import pandas as pd
from data_fetcher import get_stock_data
from strategy import VolumeBreakoutStrategy
from config import STRATEGY_PARAMS

# 获取数据
symbol = "000001"
df = get_stock_data(symbol, "20240101", "20250131")

if df is not None:
    print(f"数据总行数: {len(df)}")
    print("\n" + "="*80)

    # 测试1：hold_days=1
    print("\n【测试1】hold_days=1 的情况")
    print("="*80)
    params_1day = STRATEGY_PARAMS.copy()
    params_1day['hold_days'] = 1
    strategy_1day = VolumeBreakoutStrategy(params_1day)

    df_signals_1day = strategy_1day.calculate_signals(df)

    # 找出Buy_Signal和Sell_Signal的位置
    buy_indices_1day = df_signals_1day[df_signals_1day['Buy_Signal']].index.tolist()
    sell_indices_1day = df_signals_1day[df_signals_1day['Sell_Signal']].index.tolist()

    print(f"Buy信号个数: {len(buy_indices_1day)}")
    print(f"Sell信号个数: {len(sell_indices_1day)}")

    if buy_indices_1day:
        print(f"\n前5个Buy信号的索引: {buy_indices_1day[:5]}")
    if sell_indices_1day:
        print(f"前5个Sell信号的索引: {sell_indices_1day[:5]}")

    # 检查买卖对应关系
    if len(buy_indices_1day) > 0:
        first_buy_idx = buy_indices_1day[0]
        print(f"\n【第一个买入信号】")
        print(f"  买入索引: {first_buy_idx}")
        print(f"  买入日期: {df_signals_1day.loc[first_buy_idx, '日期']}")
        print(f"  买入价: {df_signals_1day.loc[first_buy_idx, '收盘']:.2f}元")

        if first_buy_idx + 1 < len(df_signals_1day):
            next_idx = first_buy_idx + 1
            print(f"\n  下一个交易日（索引+1={next_idx}）:")
            print(f"    日期: {df_signals_1day.loc[next_idx, '日期']}")
            print(f"    收盘价: {df_signals_1day.loc[next_idx, '收盘']:.2f}元")
            print(f"    Sell_Signal: {df_signals_1day.loc[next_idx, 'Sell_Signal']}")

    trades_1day = strategy_1day.get_trades(df)
    print(f"\n回测结果（hold_days=1）:")
    print(f"  总交易数: {len(trades_1day)}")
    if trades_1day:
        print(f"  平均收益率: {pd.DataFrame(trades_1day)['收益率%'].mean():.4f}%")
        print(f"\n前3笔交易:")
        for idx, trade in enumerate(trades_1day[:3]):
            print(f"    交易{idx+1}: {trade['买入日期']} ({trade['买入价']:.2f}元) -> "
                  f"{trade['卖出日期']} ({trade['卖出价']:.2f}元), "
                  f"收益率: {trade['收益率%']:.4f}%")

    # 测试2：hold_days=3
    print("\n\n" + "="*80)
    print("【测试2】hold_days=3 的情况")
    print("="*80)
    params_3day = STRATEGY_PARAMS.copy()
    params_3day['hold_days'] = 3
    strategy_3day = VolumeBreakoutStrategy(params_3day)

    df_signals_3day = strategy_3day.calculate_signals(df)

    buy_indices_3day = df_signals_3day[df_signals_3day['Buy_Signal']].index.tolist()
    sell_indices_3day = df_signals_3day[df_signals_3day['Sell_Signal']].index.tolist()

    print(f"Buy信号个数: {len(buy_indices_3day)}")
    print(f"Sell信号个数: {len(sell_indices_3day)}")

    if buy_indices_3day:
        print(f"\n前5个Buy信号的索引: {buy_indices_3day[:5]}")
    if sell_indices_3day:
        print(f"前5个Sell信号的索引: {sell_indices_3day[:5]}")

    # 检查买卖对应关系
    if len(buy_indices_3day) > 0:
        first_buy_idx = buy_indices_3day[0]
        print(f"\n【第一个买入信号】")
        print(f"  买入索引: {first_buy_idx}")
        print(f"  买入日期: {df_signals_3day.loc[first_buy_idx, '日期']}")
        print(f"  买入价: {df_signals_3day.loc[first_buy_idx, '收盘']:.2f}元")

        if first_buy_idx + 3 < len(df_signals_3day):
            next_idx = first_buy_idx + 3
            print(f"\n  3个交易日后（索引+3={next_idx}）:")
            print(f"    日期: {df_signals_3day.loc[next_idx, '日期']}")
            print(f"    收盘价: {df_signals_3day.loc[next_idx, '收盘']:.2f}元")
            print(f"    Sell_Signal: {df_signals_3day.loc[next_idx, 'Sell_Signal']}")

    trades_3day = strategy_3day.get_trades(df)
    print(f"\n回测结果（hold_days=3）:")
    print(f"  总交易数: {len(trades_3day)}")
    if trades_3day:
        print(f"  平均收益率: {pd.DataFrame(trades_3day)['收益率%'].mean():.4f}%")
        print(f"\n前3笔交易:")
        for idx, trade in enumerate(trades_3day[:3]):
            print(f"    交易{idx+1}: {trade['买入日期']} ({trade['买入价']:.2f}元) -> "
                  f"{trade['卖出日期']} ({trade['卖出价']:.2f}元), "
                  f"收益率: {trade['收益率%']:.4f}%")

    # 对比分析
    print("\n\n" + "="*80)
    print("【对比分析】")
    print("="*80)

    if trades_1day and trades_3day:
        df_trades_1day = pd.DataFrame(trades_1day)
        df_trades_3day = pd.DataFrame(trades_3day)

        avg_return_1day = df_trades_1day['收益率%'].mean()
        avg_return_3day = df_trades_3day['收益率%'].mean()

        print(f"hold_days=1 平均收益率: {avg_return_1day:.4f}%")
        print(f"hold_days=3 平均收益率: {avg_return_3day:.4f}%")
        print(f"差异: {abs(avg_return_1day - avg_return_3day):.4f}%")

        if abs(avg_return_1day - avg_return_3day) < 0.01:
            print("\n❌ 问题确认：两者收益率完全相同！这是一个严重的bug！")
            print("\n可能的原因:")
            print("1. 卖出信号的索引计算错误（使用绝对索引而不是交易日计数）")
            print("2. 索引中包含NaN或被重置")
            print("3. 卖出逻辑没有正确处理持股天数")
        else:
            print(f"\n✓ 收益率存在差异，系统工作正常")
