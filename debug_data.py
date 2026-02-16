"""调试脚本 - 检查akshare数据格式"""
import akshare as ak

print("测试akshare数据格式...")
print()

# 尝试获取一只股票的数据
symbol = "000001"
start_date = "20240101"
end_date = "20250213"

print(f"获取 {symbol} 的数据...")
df = ak.stock_zh_a_hist(
    symbol=symbol,
    start_date=start_date,
    end_date=end_date,
    adjust="qfq"
)

print(f"\n数据形状: {df.shape}")
print(f"列数: {len(df.columns)}")
print(f"列名: {df.columns.tolist()}")
print(f"\n前3行数据:")
print(df.head(3))
print(f"\n数据类型:")
print(df.dtypes)
