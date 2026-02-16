"""诊断回测数据问题"""
import pandas as pd
from datetime import datetime
from data_manager import DataManager
from strategy import VolumeBreakoutStrategy
from backtest_engine import BacktestEngine
from config import STRATEGY_PARAMS

print("="*80)
print("  回测数据诊断工具")
print("="*80)
print()

# 初始化
manager = DataManager()
strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
engine = BacktestEngine()

# 获取缓存中的第一只股票
print("✓ 检查缓存数据")
print()

import sqlite3
from pathlib import Path

# 确保连接到正确的数据库文件位置
db_file = Path("./data_cache/stock_data.db")
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

if not tables:
    print("❌ 数据库为空，没有任何表")
    print()
    print("解决方案：")
    print("  1. 打开浏览器访问 http://localhost:5000")
    print("  2. 进入\"📊 数据管理\"标签")
    print("  3. 选择板块和数量，点击\"获取数据\"")
    print("  4. 等待数据获取完成后重新运行此脚本")
    conn.close()
    exit(1)

# 查询有多少只股票的数据
cursor.execute("SELECT DISTINCT symbol FROM stock_data LIMIT 1")
result = cursor.fetchone()

if not result:
    print("❌ stock_data表存在但没有任何数据")
    print()
    print("解决方案：同上")
    conn.close()
    exit(1)

symbol = result[0]
print(f"✓ 发现股票数据: {symbol}")
print()

# 获取该股票的数据
df = manager.get_data_from_cache(symbol)

if df is None or len(df) == 0:
    print(f"❌ 无法从缓存获取{symbol}的数据")
    conn.close()
    exit(1)

print(f"✓ 成功获取{symbol}的{len(df)}条数据")
print()

# 检查数据质量
print("数据质量检查：")
print("-" * 80)
print()

# 1. 检查列名
print(f"1. 列名: {', '.join(df.columns.tolist())}")
print()

# 2. 检查价格数据
print("2. 价格数据:")
print(f"   收盘价 - 最小: {df['收盘'].min():.4f}, 最大: {df['收盘'].max():.4f}, 均值: {df['收盘'].mean():.4f}")
print(f"   成交量 - 最小: {df['成交量'].min():.0f}, 最大: {df['成交量'].max():.0f}, 均值: {df['成交量'].mean():.0f}")

# 检查是否全是0
if df['收盘'].sum() == 0:
    print(f"   ⚠️ 收盘价全是0！")
if df['成交量'].sum() == 0:
    print(f"   ⚠️ 成交量全是0！")

print()

# 3. 检查数据样本
print("3. 最近5条数据样本:")
sample_df = df[['日期', '开盘', '收盘', '成交量']].tail(5)
print(sample_df.to_string())
print()

# 4. 运行策略计算
print("策略信号检查：")
print("-" * 80)
print()

signals_df = strategy.calculate_signals(df)

print(f"1. MA30向上信号: {signals_df['MA30_Up'].sum()}/{len(df)} ({signals_df['MA30_Up'].sum()/len(df)*100:.1f}%)")
print(f"2. 量能放大信号: {signals_df['Volume_Surge'].sum()}/{len(df)} ({signals_df['Volume_Surge'].sum()/len(df)*100:.1f}%)")
print(f"3. 5日线回踩信号: {signals_df['MA5_Retest'].sum()}/{len(df)} ({signals_df['MA5_Retest'].sum()/len(df)*100:.1f}%)")
print(f"4. 综合买入信号: {signals_df['Buy_Signal'].sum()}/{len(df)} ({signals_df['Buy_Signal'].sum()/len(df)*100:.1f}%)")
print()

# 5. 回测结果
print("回测结果：")
print("-" * 80)
print()

result = engine.run_single_stock(symbol, df, strategy)

print(f"1. 交易笔数: {result['num_trades']}")
print(f"2. 总收益率: {result['total_return']:.2f}%")
print(f"3. 平均收益: {result['avg_return']:.2f}%")
print(f"4. 胜率: {result['win_rate']:.1f}%")
print()

# 6. 问题诊断
print("问题诊断：")
print("-" * 80)
print()

issues = []

if df['收盘'].sum() == 0:
    issues.append("❌ 收盘价全是0 - 数据获取失败")
if df['成交量'].sum() == 0:
    issues.append("❌ 成交量全是0 - 数据获取失败")
if signals_df['Buy_Signal'].sum() == 0:
    issues.append("⚠️ 没有买入信号 - 需要调整参数或检查数据")
if result['num_trades'] == 0:
    issues.append("⚠️ 没有交易 - 可能是参数过于严格")

if not issues:
    print("✅ 数据和策略正常，已生成交易信号")
else:
    print("发现的问题：")
    for issue in issues:
        print(f"  {issue}")
    print()
    print("解决建议：")
    if "数据获取失败" in str(issues):
        print("  • 检查网络连接")
        print("  • 尝试重新获取数据")
        print("  • 使用不同的股票代码")
    if "没有买入信号" in str(issues):
        print("  • 参数可能过于严格")
        print("  • 尝试减小volume_multiplier")
        print("  • 访问 http://localhost:5000/parameters 调整参数")

print()
conn.close()

print("="*80)
print("  诊断完成")
print("="*80)
