"""可视化模块"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def plot_stock_with_signals(df: pd.DataFrame, symbol: str, title: str = ""):
    """绘制股票价格和交易信号"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [3, 1]})

    # 上图：价格和均线
    ax1.plot(df['日期'], df['收盘'], label='收盘价', linewidth=1.5, color='black')
    ax1.plot(df['日期'], df['MA5'], label='MA5', linewidth=1, alpha=0.7, color='orange')
    ax1.plot(df['日期'], df['MA30'], label='MA30', linewidth=1.5, alpha=0.7, color='red')

    # 标记买入和卖出
    buy_points = df[df['Buy_Signal']]
    sell_points = df[df['Sell_Signal']]

    ax1.scatter(buy_points['日期'], buy_points['收盘'], marker='^', color='green',
               s=100, label='买入', zorder=5)
    ax1.scatter(sell_points['日期'], sell_points['收盘'], marker='v', color='red',
               s=100, label='卖出', zorder=5)

    ax1.set_title(f'{symbol} - {title}', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # 下图：成交量
    colors = ['green' if df.loc[i, '收盘'] >= df.loc[i, '开盘'] else 'red'
              for i in range(len(df))]
    ax2.bar(df['日期'], df['成交量'], color=colors, alpha=0.6, width=1)
    if 'BaseVol_MA' in df.columns:
        ax2.plot(df['日期'], df['BaseVol_MA'], label='20日均量', color='blue', linewidth=1.5)
        ax2.axhline(y=df['BaseVol_MA'].mean() * 2, color='orange', linestyle='--',
                   label='量能放大线', alpha=0.7)

    ax2.set_title('成交量', fontsize=12)
    ax2.set_ylabel('成交量(手)', fontsize=10)
    ax2.set_xlabel('日期', fontsize=10)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_results_summary(aggregated: dict, index_name: str = ""):
    """绘制回测结果摘要"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'回测结果摘要 - {index_name}', fontsize=14, fontweight='bold')

    # 1. 关键指标
    ax = axes[0, 0]
    ax.axis('off')
    metrics_text = f"""
    总交易数: {aggregated['total_trades']}
    覆盖股票数: {aggregated['stocks_count']}
    总收益: {aggregated['total_return']:.2f}%
    平均单笔收益: {aggregated['avg_return_per_trade']:.2f}%
    胜率: {aggregated['win_rate']:.1f}%
    盈亏比: {aggregated['profit_factor']:.2f}
    """
    ax.text(0.1, 0.5, metrics_text, fontsize=12, verticalalignment='center',
           family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 2. 收益分布
    ax = axes[0, 1]
    # 这里需要有具体的交易数据，暂时显示柱子
    categories = ['总收益', '平均收益', '最大收益', '最小收益']
    values = [
        aggregated['total_return'],
        aggregated['avg_return_per_trade'],
        aggregated['max_single_return'],
        aggregated['min_single_return']
    ]
    colors_bar = ['green' if v > 0 else 'red' for v in values]
    ax.bar(categories, values, color=colors_bar, alpha=0.7)
    ax.set_ylabel('收益率 (%)', fontsize=10)
    ax.set_title('收益分布', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(values):
        ax.text(i, v, f'{v:.1f}%', ha='center', va='bottom' if v > 0 else 'top')

    # 3. 胜负统计
    ax = axes[1, 0]
    win_pct = aggregated['win_rate']
    loss_pct = 100 - win_pct
    colors_pie = ['green', 'red']
    ax.pie([win_pct, loss_pct], labels=['获胜', '亏损'],
          autopct='%1.1f%%', colors=colors_pie, startangle=90)
    ax.set_title('胜负比例', fontsize=12)

    # 4. 其他指标
    ax = axes[1, 1]
    ax.axis('off')
    other_text = f"""
    最大单笔收益: {aggregated['max_single_return']:.2f}%
    最大单笔亏损: {aggregated['min_single_return']:.2f}%
    平均获利: {aggregated['avg_profit']:.2f}%
    平均亏损: {aggregated['avg_loss']:.2f}%
    """
    ax.text(0.1, 0.5, other_text, fontsize=12, verticalalignment='center',
           family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    plt.tight_layout()
    return fig


def save_trades_to_csv(trades: list, symbol: str, output_file: str = None):
    """保存交易记录到CSV"""
    if not trades:
        return None

    df = pd.DataFrame(trades)
    if output_file is None:
        output_file = f'trades_{symbol}.csv'

    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    return output_file
