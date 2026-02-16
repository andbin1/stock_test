"""测试 efinance 真实数据获取"""
import sys

print("=" * 80)
print("  efinance 真实A股数据测试")
print("=" * 80)
print()

# 测试导入
try:
    import efinance as ef
    print("✓ efinance 库已安装")
except ImportError:
    print("❌ efinance 库未安装")
    print("   运行: pip install efinance")
    sys.exit(1)

print()

# 尝试获取数据
print("尝试获取真实数据...")
print()

symbols = ["000001", "000651", "000858"]

for symbol in symbols:
    print(f"测试 {symbol}...", end=" ")

    try:
        df = ef.stock.get_quote_history(symbol, beg='20250201', end='20250213')

        if df is not None and len(df) > 0:
            print(f"✓ 成功 ({len(df)} 条数据)")
        else:
            print("❌ 无数据")

    except Exception as e:
        error_msg = str(e)
        if 'ConnectionError' in error_msg or 'Connection' in error_msg:
            print("❌ 网络连接失败")
        elif 'Timeout' in error_msg:
            print("❌ 请求超时")
        else:
            print(f"❌ 错误: {error_msg[:30]}")

print()
print("=" * 80)
print()

# 检查网络
print("网络诊断:")
print()

import socket

try:
    socket.gethostbyname('push2his.eastmoney.com')
    print("✓ 可以解析 push2his.eastmoney.com")
except socket.gaierror:
    print("❌ 无法解析 push2his.eastmoney.com")
    print("   (可能是网络或DNS问题)")

print()

# 建议
print("=" * 80)
print("建议:")
print()
print("✓ 如果所有测试都成功:")
print("   运行: python main.py")
print("   获得完整的真实数据回测结果")
print()
print("❌ 如果所有测试都失败:")
print("   1. 检查网络连接")
print("   2. 尝试 ping push2his.eastmoney.com")
print("   3. 如果 ping 不通，可能需要配置VPN/代理")
print("   4. 继续使用演示数据: python quick_excel_export.py")
print()
print("=" * 80)
