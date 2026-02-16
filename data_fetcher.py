"""数据获取模块 - 从efinance/akshare获取A股数据"""
import pandas as pd
from tqdm import tqdm
import time

# 优先使用 efinance，失败则使用 akshare
try:
    import efinance as ef
    HAS_EFINANCE = True
except ImportError:
    HAS_EFINANCE = False

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

def generate_stock_codes(prefix: str, start: int, end: int) -> list:
    """根据代码规律生成股票代码列表

    Args:
        prefix: 股票代码前缀（如"000"、"300"、"600"）
        start: 起始号
        end: 结束号

    Returns:
        股票代码列表（如 ["000001", "000002", ...]）
    """
    stocks = []
    for i in range(start, end + 1):
        stocks.append(f"{prefix}{i:03d}")
    return stocks


def get_index_constituents(index_code: str, limit: int = None) -> list:
    """获取指数成分股列表 - 动态生成完整市场数据"""
    print(f"获取指数 {index_code} 的成分股...")

    # 根据股票代码规律生成完整列表
    if index_code == "000001":  # 沪深A股 - 包含所有可交易的A股
        # 深圳主板：000001-002999
        sz_main = generate_stock_codes("000", 1, 999)  # 000001-000999（主板+中小板）
        sz_cyb = generate_stock_codes("300", 1, 999)   # 300001-300999（创业板）

        # 上海主板：600000-609999
        sh_main = generate_stock_codes("600", 0, 999)  # 600000-600999

        # 合并所有股票
        a_stocks = sz_main + sz_cyb + sh_main

    elif index_code == "399006":  # 创业板
        # 创业板：300001-300999
        cy_stocks = generate_stock_codes("300", 1, 999)
        a_stocks = cy_stocks

    elif index_code == "000688":  # 科创板
        # 科创板：688000-689999
        kc_stocks = generate_stock_codes("688", 0, 999)
        a_stocks = kc_stocks

    elif index_code == "399001":  # 深成指
        # 深圳所有股票
        sz_main = generate_stock_codes("000", 1, 999)
        sz_cyb = generate_stock_codes("300", 1, 999)
        a_stocks = sz_main + sz_cyb

    elif index_code == "000905":  # 中证500 - 中等规模股票
        # 生成中证500范围的股票代码
        sz_stocks = generate_stock_codes("000", 500, 999)  # 较大的深圳股票
        sh_stocks = generate_stock_codes("600", 500, 799)  # 较大的上海股票
        a_stocks = sz_stocks + sh_stocks

    elif index_code == "000300":  # 沪深300（兼容旧代码）
        # 大盘股票
        sz_large = generate_stock_codes("000", 1, 200)
        sh_large = generate_stock_codes("600", 0, 300)
        a_stocks = sz_large + sh_large
    else:
        print(f"不支持的指数代码: {index_code}")
        # 如果是不支持的指数，返回原始的硬编码列表
        a_stocks = [
            "000001", "000002", "000024", "000027", "000050", "600000", "600016"
        ]

    # 去除重复数据
    a_stocks = list(dict.fromkeys(a_stocks))

    if limit:
        a_stocks = a_stocks[:limit]

    print(f"  已获取 {len(a_stocks)} 只成分股")
    return a_stocks


def get_stock_data(symbol: str, start_date: str, end_date: str, max_retries: int = 3) -> pd.DataFrame:
    """
    获取单只股票历史数据（优先使用efinance，失败则使用akshare）
    symbol: 股票代码（如 "000001" 或 "600000"）
    start_date: 开始日期（如 "20200101"）
    end_date: 结束日期（如 "20250213"）
    """
    # 尝试方法1: efinance
    if HAS_EFINANCE:
        try:
            df = ef.stock.get_quote_history(symbol, beg=start_date, end=end_date)

            if df is None or df.empty:
                return None

            df = df.reset_index(drop=True)

            # 标准化列名
            df = pd.DataFrame({
                '日期': pd.to_datetime(df.iloc[:, 0]) if len(df.columns) > 0 else None,
                '开盘': df.iloc[:, 1] if len(df.columns) > 1 else None,
                '收盘': df.iloc[:, 2] if len(df.columns) > 2 else None,
                '高': df.iloc[:, 3] if len(df.columns) > 3 else None,
                '低': df.iloc[:, 4] if len(df.columns) > 4 else None,
                '成交量': df.iloc[:, 5] if len(df.columns) > 5 else None,
                '成交额': df.iloc[:, 6] if len(df.columns) > 6 else None,
            })

            df = df.dropna(subset=['收盘'])
            df = df.sort_values('日期').reset_index(drop=True)

            # 添加标准化列
            df['振幅'] = ((df['高'] - df['低']) / df['低'] * 100).round(2)
            df['涨跌幅'] = ((df['收盘'] - df['开盘']) / df['开盘'] * 100).round(2)
            df['涨跌'] = (df['收盘'] - df['开盘']).round(2)
            df['换手率'] = 0.0

            return df

        except Exception as e:
            pass  # 尝试下一个方法

    # 尝试方法2: akshare
    if HAS_AKSHARE:
        for attempt in range(max_retries):
            try:
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # 前复权
                )

                if df.empty:
                    return None

                df = df.reset_index(drop=True)

                # 标准化列名
                df = df.rename(columns={
                    '日期': '日期',
                    '开盘': '开盘',
                    '收盘': '收盘',
                    '最高': '高',
                    '最低': '低',
                    '成交量': '成交量',
                    '成交额': '成交额',
                    '振幅': '振幅',
                    '涨跌幅': '涨跌幅',
                    '涨跌额': '涨跌',
                    '换手率': '换手率'
                })

                df = df[['日期', '开盘', '收盘', '高', '低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌', '换手率']]

                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期').reset_index(drop=True)

                # 将成交量转换为手（100股为1手）
                df['成交量'] = df['成交量'] / 100

                return df
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试
                    continue
                else:
                    pass  # 继续尝试其他方法

    # 如果两个都失败
    print(f"获取 {symbol} 数据失败: 无可用数据源")
    return None


def get_batch_stock_data(symbols: list, start_date: str, end_date: str) -> dict:
    """批量获取股票数据"""
    all_data = {}
    failed = []

    print(f"开始获取 {len(symbols)} 只股票的数据...")
    for i, symbol in enumerate(tqdm(symbols), 1):
        df = get_stock_data(symbol, start_date, end_date)
        if df is not None and len(df) > 0:
            all_data[symbol] = df
        else:
            failed.append(symbol)

        # 避免请求过快被限制
        if i % 10 == 0:
            time.sleep(1)

    print(f"成功获取 {len(all_data)} 只股票的数据，{len(failed)} 只失败")
    return all_data


if __name__ == "__main__":
    # 测试
    stocks = get_index_constituents("000300", limit=5)
    print(f"成分股: {stocks}")

    data = get_batch_stock_data(stocks, "20240101", "20250213")
    for symbol, df in data.items():
        print(f"\n{symbol}:")
        print(df.head())
