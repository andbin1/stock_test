"""使用 efinance 库获取A股数据（推荐方式）"""
import pandas as pd
import efinance as ef
import time
from tqdm import tqdm


def get_stock_data_efinance(symbol: str, start_date: str, end_date: str, max_retries: int = 3) -> pd.DataFrame:
    """
    使用 efinance 获取单只股票历史数据

    参数:
        symbol: 股票代码（如 "000001"）
        start_date: 开始日期（如 "20200101"）
        end_date: 结束日期（如 "20250213"）
        max_retries: 最大重试次数

    返回:
        DataFrame，包含 OHLCV 数据
    """
    # 转换日期格式：20200101 -> 2020-01-01（efinance 需要这个格式，但实际上接受 20200101）
    for attempt in range(max_retries):
        try:
            print(f"  [efinance] 获取 {symbol}...", end=" ")

            # 调用 efinance API
            df = ef.stock.get_quote_history(
                symbol,
                beg=start_date,
                end=end_date
            )

            if df is None or df.empty:
                print("无数据")
                return None

            print(f"✓ {len(df)} 条")

            # 标准化列名和数据
            df_normalized = pd.DataFrame({
                '日期': pd.to_datetime(df.iloc[:, 0]) if len(df.columns) > 0 else None,
                '开盘': df.iloc[:, 1] if len(df.columns) > 1 else None,
                '收盘': df.iloc[:, 2] if len(df.columns) > 2 else None,
                '高': df.iloc[:, 3] if len(df.columns) > 3 else None,
                '低': df.iloc[:, 4] if len(df.columns) > 4 else None,
                '成交量': df.iloc[:, 5] if len(df.columns) > 5 else None,
                '成交额': df.iloc[:, 6] if len(df.columns) > 6 else None,
            })

            # 如果列名不对，尝试通过列索引访问
            if df_normalized['开盘'].isna().all():
                # 尝试使用原始列名
                df_normalized = df.copy()
                # 重命名为标准列名
                col_mapping = {}
                col_names = df.columns.tolist()

                if '开' in str(col_names) or '开盘' in str(col_names):
                    # 尝试匹配列名
                    for i, col in enumerate(col_names):
                        if '日期' in col or 'date' in col.lower():
                            df_normalized['日期'] = df.iloc[:, i]
                        elif '开' in col:
                            df_normalized['开盘'] = df.iloc[:, i]
                        elif '收' in col:
                            df_normalized['收盘'] = df.iloc[:, i]
                        elif '高' in col or '最高' in col:
                            df_normalized['高'] = df.iloc[:, i]
                        elif '低' in col or '最低' in col:
                            df_normalized['低'] = df.iloc[:, i]
                        elif '量' in col or '成交量' in col:
                            df_normalized['成交量'] = df.iloc[:, i]
                        elif '额' in col or '成交额' in col:
                            df_normalized['成交额'] = df.iloc[:, i]

            # 数据清理
            df_normalized = df_normalized[['日期', '开盘', '收盘', '高', '低', '成交量', '成交额']].copy()
            df_normalized['日期'] = pd.to_datetime(df_normalized['日期'])
            df_normalized = df_normalized.dropna(subset=['收盘'])
            df_normalized = df_normalized.sort_values('日期').reset_index(drop=True)

            # 添加标准化的其他列（为了兼容旧代码）
            df_normalized['振幅'] = ((df_normalized['高'] - df_normalized['低']) / df_normalized['低'] * 100).round(2)
            df_normalized['涨跌幅'] = ((df_normalized['收盘'] - df_normalized['开盘']) / df_normalized['开盘'] * 100).round(2)
            df_normalized['涨跌'] = (df_normalized['收盘'] - df_normalized['开盘']).round(2)
            df_normalized['换手率'] = 0.0  # efinance 不提供换手率

            return df_normalized

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避：2s, 4s, 8s
                print(f"重试中... (等待{wait_time}s)")
                time.sleep(wait_time)
            else:
                print(f"失败: {str(e)[:50]}")
                return None

    return None


def get_batch_stock_data_efinance(symbols: list, start_date: str, end_date: str) -> dict:
    """批量获取多只股票的数据"""
    all_data = {}
    failed = []

    print(f"使用 efinance 获取 {len(symbols)} 只股票数据...")
    print()

    for i, symbol in enumerate(tqdm(symbols), 1):
        df = get_stock_data_efinance(symbol, start_date, end_date)
        if df is not None and len(df) > 0:
            all_data[symbol] = df
        else:
            failed.append(symbol)

        # 避免请求过快
        if i % 5 == 0:
            time.sleep(1)

    print()
    print(f"成功: {len(all_data)} 只，失败: {len(failed)} 只")

    if failed:
        print(f"失败的股票: {', '.join(failed[:10])}")
        if len(failed) > 10:
            print(f"... 还有 {len(failed) - 10} 只")

    return all_data


if __name__ == "__main__":
    # 测试
    print("测试 efinance 数据获取...")
    print()

    stock = "000001"
    print(f"获取 {stock} 的数据...")

    df = get_stock_data_efinance(stock, "20250101", "20250213")

    if df is not None:
        print()
        print(f"数据形状: {df.shape}")
        print()
        print("前5行:")
        print(df.head())
    else:
        print("获取失败")
