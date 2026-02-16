"""快速生成Excel报告 - 用于校对交易明细"""
import sys
from demo_test_debug import generate_better_mock_data
from export_to_excel import export_detailed_trades_to_excel

print("=" * 80)
print("  快速生成Excel交易明细报告")
print("=" * 80)
print()

# 生成5个示例股票
stocks = ["000001", "000651", "000858", "600000", "601399"]

print(f"生成 {len(stocks)} 个股票的详细Excel报告...\n")

for idx, stock_code in enumerate(stocks, 1):
    try:
        print(f"[{idx}/{len(stocks)}] 处理 {stock_code}...")

        # 生成模拟数据
        df = generate_better_mock_data(stock_code, days=250)

        # 导出Excel
        output_file = export_detailed_trades_to_excel(
            stock_code, df,
            output_file=f'交易明细_{stock_code}.xlsx'
        )

        print(f"      ✓ 生成成功")

    except Exception as e:
        print(f"      ❌ 错误: {e}")

print()
print("=" * 80)
print("✅ 完成生成所有Excel文件！")
print("=" * 80)
print()
print("📂 生成的文件列表:")
for stock_code in stocks:
    print(f"  • 交易明细_{stock_code}.xlsx")

print()
print("📋 每个Excel文件包含4个Sheet页:")
print()
print("  1️⃣  【交易摘要】")
print("      ├─ 股票信息（代码、数据范围）")
print("      └─ 统计数据（交易数、总收益、平均收益、胜率等）")
print()
print("  2️⃣  【交易清单】- 用于校对 ✓")
print("      ├─ 序号")
print("      ├─ 股票代码")
print("      ├─ 买入日期、买入时间、买入价格")
print("      ├─ 卖出日期、卖出时间、卖出价格")
print("      ├─ 持有天数")
print("      ├─ 收益率%（绿色=盈利，红色=亏损）")
print("      └─ 状态（平仓/未平仓）")
print()
print("  3️⃣  【信号点详情】- 用于验证策略条件")
print("      ├─ 日期、收盘价、MA5、MA30")
print("      ├─ 成交量、MA20均量")
print("      ├─ 条件标记（MA30向上、量能放大、5日线回踩）")
print("      ├─ BUY信号（绿色）")
print("      └─ SELL信号（红色）")
print()
print("  4️⃣  【策略参数】")
print("      └─ 回测使用的参数配置")
print()
print("=" * 80)
print("💡 用法：")
print()
print("  1. 用Excel打开 交易明细_*.xlsx")
print("  2. 查看【交易清单】Sheet页")
print("  3. 校对买入/卖出的时间和价格")
print("  4. 如果需要调整策略，修改config.py后重新生成")
print()
print("  运行以下命令生成新报告：")
print("    python quick_excel_export.py")
print()
print("=" * 80)
