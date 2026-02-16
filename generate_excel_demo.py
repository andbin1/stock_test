"""生成演示Excel文件 - 展示导出功能"""
import sys
from demo_test_debug import generate_better_mock_data
from export_to_excel import export_detailed_trades_to_excel

print("=" * 80)
print("  生成演示Excel文件")
print("=" * 80)
print()

# 生成模拟数据
symbol = "demo_000001"
print(f"生成模拟股票 {symbol} 的数据...")
df = generate_better_mock_data(symbol, days=250)

# 导出Excel
print(f"导出回测结果到Excel...")
try:
    output_file = export_detailed_trades_to_excel(symbol, df, output_file=f"演示回测_{symbol}.xlsx")
    print()
    print("=" * 80)
    print(f"✅ 成功生成: {output_file}")
    print("=" * 80)
    print()
    print("📊 Excel文件包含以下4个Sheet页:")
    print()
    print("  1️⃣  【交易摘要】")
    print("      • 股票代码和数据范围")
    print("      • 交易总数、总收益率、平均收益、胜率等统计")
    print()
    print("  2️⃣  【交易清单】")
    print("      • 每笔交易的详细信息")
    print("      • 序号 | 股票代码 | 买入日期 | 买入时间 | 买入价")
    print("      • 卖出日期 | 卖出时间 | 卖出价 | 持有天数 | 收益率% | 状态")
    print("      • 绿色表示盈利，红色表示亏损")
    print()
    print("  3️⃣  【信号点详情】")
    print("      • 所有满足策略条件的交易点")
    print("      • 日期 | 收盘价 | MA5 | MA30 | 成交量 | MA20均量")
    print("      • 显示MA30向上、量能放大、5日线回踩等各个条件")
    print("      • 标记买入和卖出信号")
    print()
    print("  4️⃣  【策略参数】")
    print("      • 使用的回测参数配置")
    print("      • MA周期、量能倍数、持有天数等")
    print()
    print("=" * 80)
    print("💡 用法:")
    print()
    print("  1. 用Excel打开文件查看")
    print("  2. 校对每笔交易的时间和价格")
    print("  3. 如需调整参数，修改config.py后重新生成")
    print()
    print("=" * 80)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
