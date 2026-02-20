"""数据获取模块 - 从efinance获取A股数据"""
import pandas as pd
from tqdm import tqdm
import time

# 使用 efinance 作为数据源
try:
    import efinance as ef
    HAS_EFINANCE = True
except ImportError:
    HAS_EFINANCE = False
    print("错误: 未安装 efinance 库")
    print("请运行: pip install efinance")

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
        # 科创板：688001-688999（注意：688000 不存在，从 688001 开始）
        kc_stocks = generate_stock_codes("688", 1, 999)
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
    获取单只股票历史数据（使用efinance）
    symbol: 股票代码（如 "000001" 或 "600000"）
    start_date: 开始日期（如 "20200101"）
    end_date: 结束日期（如 "20250213"）
    """
    if not HAS_EFINANCE:
        print(f"错误: efinance 库未安装，无法获取数据")
        return None

    # 使用 efinance 获取数据，支持重试
    for attempt in range(max_retries):
        try:
            df = ef.stock.get_quote_history(symbol, beg=start_date, end=end_date)

            if df is None or df.empty:
                return None

            df = df.reset_index(drop=True)

            # 标准化列名（使用列名而非索引，更稳定）
            # efinance 返回的列：['股票名称', '股票代码', '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            df = pd.DataFrame({
                '日期': pd.to_datetime(df['日期'], errors='coerce') if '日期' in df.columns else None,
                '开盘': df['开盘'] if '开盘' in df.columns else None,
                '收盘': df['收盘'] if '收盘' in df.columns else None,
                '高': df['最高'] if '最高' in df.columns else None,
                '低': df['最低'] if '最低' in df.columns else None,
                '成交量': df['成交量'] if '成交量' in df.columns else None,
                '成交额': df['成交额'] if '成交额' in df.columns else None,
                '振幅': df['振幅'] if '振幅' in df.columns else None,
                '涨跌幅': df['涨跌幅'] if '涨跌幅' in df.columns else None,
                '涨跌': df['涨跌额'] if '涨跌额' in df.columns else None,
                '换手率': df['换手率'] if '换手率' in df.columns else None,
            })

            # 删除日期无效的行
            df = df.dropna(subset=['日期', '收盘'])
            df = df.sort_values('日期').reset_index(drop=True)

            # efinance 已提供所有指标，无需重复计算
            # 只需确保数据类型正确
            return df

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # 等待2秒后重试
                continue
            else:
                print(f"获取 {symbol} 数据失败: {str(e)}")
                return None

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
