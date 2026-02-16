"""
新策略演示脚本
展示如何使用双均线、网格交易、海龟交易三个策略
"""
import sys
import pandas as pd
from datetime import datetime

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
    TURTLE_TRADING_PARAMS,
    NEW_STRATEGY_MAP
)

# 导入数据获取模块
try:
    from data_fetcher import get_stock_data
except ImportError:
    print("警告：无法导入data_fetcher，使用模拟数据")
    get_stock_data = None


def print_separator(title="", char="=", length=80):
    """打印分隔线"""
    if title:
        print(f"\n{char * length}")
        print(f" {title}")
        print(char * length)
    else:
        print(char * length)


def analyze_trades(trades, strategy_name):
    """分析交易结果"""
    if not trades:
        print(f"\n{strategy_name}：无交易信号")
        return

    trades_df = pd.DataFrame(trades)

    print(f"\n{strategy_name}：")
    print(f"{'=' * 60}")

    # 基本统计
    print(f"\n【交易统计】")
    print(f"  交易次数：{len(trades)} 笔")
    print(f"  平均收益率：{trades_df['收益率%'].mean():.2f}%")
    print(f"  中位数收益率：{trades_df['收益率%'].median():.2f}%")

    # 盈亏分析
    winning_trades = trades_df[trades_df['收益率%'] > 0]
    losing_trades = trades_df[trades_df['收益率%'] <= 0]

    win_count = len(winning_trades)
    lose_count = len(losing_trades)
    win_rate = (win_count / len(trades) * 100) if len(trades) > 0 else 0

    print(f"\n【盈亏分析】")
    print(f"  盈利次数：{win_count} 笔")
    print(f"  亏损次数：{lose_count} 笔")
    print(f"  胜率：{win_rate:.2f}%")

    if not winning_trades.empty:
        avg_win = winning_trades['收益率%'].mean()
        max_win = winning_trades['收益率%'].max()
        print(f"  平均盈利：{avg_win:.2f}%")
        print(f"  最大盈利：{max_win:.2f}%")

    if not losing_trades.empty:
        avg_loss = losing_trades['收益率%'].mean()
        max_loss = losing_trades['收益率%'].min()
        print(f"  平均亏损：{avg_loss:.2f}%")
        print(f"  最大亏损：{max_loss:.2f}%")

    # 盈亏比
    if not winning_trades.empty and not losing_trades.empty:
        profit_loss_ratio = abs(winning_trades['收益率%'].mean() / losing_trades['收益率%'].mean())
        print(f"  盈亏比：{profit_loss_ratio:.2f}:1")

    # 持仓时间
    print(f"\n【持仓分析】")
    print(f"  平均持仓天数：{trades_df['持有天数'].mean():.1f} 天")
    print(f"  最长持仓：{trades_df['持有天数'].max()} 天")
    print(f"  最短持仓：{trades_df['持有天数'].min()} 天")

    # 卖出原因统计
    if '状态' in trades_df.columns:
        print(f"\n【卖出原因】")
        status_counts = trades_df['状态'].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}：{count} 次 ({count/len(trades)*100:.1f}%)")

    # 最近交易
    print(f"\n【最近5笔交易】")
    recent_trades = trades_df.tail(5)[['买入日期', '买入价', '卖出日期', '卖出价', '收益率%', '状态']]
    print(recent_trades.to_string(index=False))


def demo_double_ma_strategy(stock_code="000001", start_date="20240101", end_date="20250213"):
    """演示双均线策略"""
    print_separator("双均线交叉策略演示", "=")

    # 策略信息
    strategy_info = NEW_STRATEGY_MAP['double_ma_cross']
    print(f"\n策略名称：{strategy_info['name']}")
    print(f"策略描述：{strategy_info['description']}")
    print(f"适用市场：{strategy_info['适用市场']}")
    print(f"风险等级：{strategy_info['风险等级']}")
    print(f"预期收益：{strategy_info['预期收益']}")
    print(f"预期胜率：{strategy_info['胜率']}")

    print(f"\n策略参数：")
    for key, value in DOUBLE_MA_PARAMS.items():
        print(f"  {key}: {value}")

    # 获取数据
    if get_stock_data is None:
        print("\n无法获取真实数据，请检查data_fetcher模块")
        return

    print(f"\n正在获取股票数据：{stock_code} ({start_date} - {end_date})...")
    df = get_stock_data(stock_code, start_date, end_date)

    if df is None or df.empty:
        print("获取数据失败")
        return

    print(f"数据获取成功，共 {len(df)} 条记录")

    # 运行策略
    print("\n正在运行双均线策略...")
    strategy = DoubleMACrossStrategy(DOUBLE_MA_PARAMS)
    trades = strategy.get_trades(df)

    # 分析结果
    analyze_trades(trades, "双均线交叉策略")


def demo_grid_trading_strategy(stock_code="000001", start_date="20240101", end_date="20250213"):
    """演示网格交易策略"""
    print_separator("网格交易策略演示", "=")

    # 策略信息
    strategy_info = NEW_STRATEGY_MAP['grid_trading']
    print(f"\n策略名称：{strategy_info['name']}")
    print(f"策略描述：{strategy_info['description']}")
    print(f"适用市场：{strategy_info['适用市场']}")
    print(f"风险等级：{strategy_info['风险等级']}")
    print(f"预期收益：{strategy_info['预期收益']}")
    print(f"预期胜率：{strategy_info['胜率']}")

    print(f"\n策略参数：")
    for key, value in GRID_TRADING_PARAMS.items():
        print(f"  {key}: {value}")

    # 获取数据
    if get_stock_data is None:
        print("\n无法获取真实数据，请检查data_fetcher模块")
        return

    print(f"\n正在获取股票数据：{stock_code} ({start_date} - {end_date})...")
    df = get_stock_data(stock_code, start_date, end_date)

    if df is None or df.empty:
        print("获取数据失败")
        return

    print(f"数据获取成功，共 {len(df)} 条记录")

    # 运行策略
    print("\n正在运行网格交易策略...")
    strategy = GridTradingStrategy(GRID_TRADING_PARAMS)
    trades = strategy.get_trades(df)

    # 分析结果
    analyze_trades(trades, "网格交易策略")


def demo_turtle_trading_strategy(stock_code="000001", start_date="20240101", end_date="20250213"):
    """演示海龟交易策略"""
    print_separator("海龟交易法则演示", "=")

    # 策略信息
    strategy_info = NEW_STRATEGY_MAP['turtle_trading']
    print(f"\n策略名称：{strategy_info['name']}")
    print(f"策略描述：{strategy_info['description']}")
    print(f"适用市场：{strategy_info['适用市场']}")
    print(f"风险等级：{strategy_info['风险等级']}")
    print(f"预期收益：{strategy_info['预期收益']}")
    print(f"预期胜率：{strategy_info['胜率']}")

    print(f"\n策略参数：")
    for key, value in TURTLE_TRADING_PARAMS.items():
        print(f"  {key}: {value}")

    # 获取数据
    if get_stock_data is None:
        print("\n无法获取真实数据，请检查data_fetcher模块")
        return

    print(f"\n正在获取股票数据：{stock_code} ({start_date} - {end_date})...")
    df = get_stock_data(stock_code, start_date, end_date)

    if df is None or df.empty:
        print("获取数据失败")
        return

    print(f"数据获取成功，共 {len(df)} 条记录")

    # 运行策略
    print("\n正在运行海龟交易策略...")
    strategy = TurtleTradingStrategy(TURTLE_TRADING_PARAMS)
    trades = strategy.get_trades(df)

    # 分析结果
    analyze_trades(trades, "海龟交易法则")


def demo_strategy_comparison(stock_code="000001", start_date="20240101", end_date="20250213"):
    """对比三个策略的表现"""
    print_separator("策略对比分析", "=")

    # 获取数据
    if get_stock_data is None:
        print("\n无法获取真实数据，请检查data_fetcher模块")
        return

    print(f"\n正在获取股票数据：{stock_code} ({start_date} - {end_date})...")
    df = get_stock_data(stock_code, start_date, end_date)

    if df is None or df.empty:
        print("获取数据失败")
        return

    print(f"数据获取成功，共 {len(df)} 条记录")

    # 运行所有策略
    strategies = [
        ("双均线交叉", DoubleMACrossStrategy(DOUBLE_MA_PARAMS)),
        ("网格交易", GridTradingStrategy(GRID_TRADING_PARAMS)),
        ("海龟交易", TurtleTradingStrategy(TURTLE_TRADING_PARAMS)),
    ]

    results = []

    for strategy_name, strategy in strategies:
        print(f"\n正在运行 {strategy_name} 策略...")
        trades = strategy.get_trades(df)

        if trades:
            trades_df = pd.DataFrame(trades)
            winning_trades = trades_df[trades_df['收益率%'] > 0]

            results.append({
                '策略': strategy_name,
                '交易次数': len(trades),
                '平均收益%': trades_df['收益率%'].mean(),
                '胜率%': len(winning_trades) / len(trades) * 100,
                '最大盈利%': trades_df['收益率%'].max(),
                '最大亏损%': trades_df['收益率%'].min(),
                '平均持仓天数': trades_df['持有天数'].mean(),
            })
        else:
            results.append({
                '策略': strategy_name,
                '交易次数': 0,
                '平均收益%': 0,
                '胜率%': 0,
                '最大盈利%': 0,
                '最大亏损%': 0,
                '平均持仓天数': 0,
            })

    # 打印对比结果
    print("\n" + "=" * 80)
    print(" 策略对比结果")
    print("=" * 80)

    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))

    # 推荐策略
    print("\n" + "=" * 80)
    print(" 策略推荐")
    print("=" * 80)

    if results:
        best_return = max(results, key=lambda x: x['平均收益%'])
        best_win_rate = max(results, key=lambda x: x['胜率%'])

        print(f"\n收益率最高：{best_return['策略']} ({best_return['平均收益%']:.2f}%)")
        print(f"胜率最高：{best_win_rate['策略']} ({best_win_rate['胜率%']:.2f}%)")


def main():
    """主函数"""
    print_separator("新策略演示系统", "=")
    print(f"\n运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 默认参数
    stock_code = "000001"  # 平安银行
    start_date = "20240101"
    end_date = "20250213"

    # 检查命令行参数
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    if len(sys.argv) > 2:
        start_date = sys.argv[2]
    if len(sys.argv) > 3:
        end_date = sys.argv[3]

    print(f"\n测试参数：")
    print(f"  股票代码：{stock_code}")
    print(f"  开始日期：{start_date}")
    print(f"  结束日期：{end_date}")

    # 选择演示模式
    print(f"\n请选择演示模式：")
    print(f"  1. 双均线交叉策略")
    print(f"  2. 网格交易策略")
    print(f"  3. 海龟交易法则")
    print(f"  4. 策略对比分析")
    print(f"  5. 运行所有演示")

    choice = input(f"\n请输入选择（1-5，默认5）：").strip()

    if not choice:
        choice = "5"

    if choice == "1":
        demo_double_ma_strategy(stock_code, start_date, end_date)
    elif choice == "2":
        demo_grid_trading_strategy(stock_code, start_date, end_date)
    elif choice == "3":
        demo_turtle_trading_strategy(stock_code, start_date, end_date)
    elif choice == "4":
        demo_strategy_comparison(stock_code, start_date, end_date)
    elif choice == "5":
        demo_double_ma_strategy(stock_code, start_date, end_date)
        demo_grid_trading_strategy(stock_code, start_date, end_date)
        demo_turtle_trading_strategy(stock_code, start_date, end_date)
        demo_strategy_comparison(stock_code, start_date, end_date)
    else:
        print("无效选择")

    print_separator("演示结束", "=")


if __name__ == "__main__":
    main()
