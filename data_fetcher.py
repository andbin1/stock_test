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


def _get_all_a_stocks_from_api() -> list:
    """通过 efinance 实时行情接口获取全量在市A股代码（沪A + 深A + 北交所）

    返回真实在市股票列表，替代按号段枚举的方式。
    失败时返回空列表，由调用方降级处理。
    """
    if not HAS_EFINANCE:
        return []
    try:
        df = ef.stock.get_realtime_quotes()
        if df is None or df.empty:
            return []
        # 只保留普通A股（沪A / 深A / 北A），过滤掉B股、基金、债券等
        if '市场类型' in df.columns:
            df = df[df['市场类型'].isin(['沪A', '深A', '北A'])]
        codes = df['股票代码'].astype(str).str.zfill(6).tolist()
        return codes
    except Exception as e:
        print(f"  [警告] 实时行情接口获取股票列表失败: {e}")
        return []


def get_index_constituents(index_code: str, limit: int = None) -> list:
    """获取指数成分股列表"""
    print(f"获取指数 {index_code} 的成分股...")

    if index_code == "000001":  # 沪深京A股全量 - 优先用API真实列表
        a_stocks = _get_all_a_stocks_from_api()
        if not a_stocks:
            # API 不可用时降级：按已知号段枚举（覆盖主要板块）
            print("  [降级] 使用号段枚举方式获取股票列表")
            a_stocks = (
                generate_stock_codes("000", 1, 999)   # 深圳主板
                + generate_stock_codes("001", 0, 999) # 深圳主板延续
                + generate_stock_codes("002", 0, 999) # 中小板
                + generate_stock_codes("003", 0, 999) # 深圳主板新股
                + generate_stock_codes("300", 0, 999) # 创业板
                + generate_stock_codes("301", 0, 999) # 创业板新股
                + generate_stock_codes("600", 0, 999) # 上海主板
                + generate_stock_codes("601", 0, 999) # 上海主板
                + generate_stock_codes("603", 0, 999) # 上海主板
                + generate_stock_codes("605", 0, 999) # 上海主板新股
                + generate_stock_codes("688", 0, 999) # 科创板
                + generate_stock_codes("689", 0, 999) # 科创板延续
            )

    elif index_code == "399006":  # 创业板
        a_stocks = _get_all_a_stocks_from_api()
        if a_stocks:
            a_stocks = [s for s in a_stocks if s.startswith(('300', '301'))]
        else:
            a_stocks = (generate_stock_codes("300", 0, 999)
                        + generate_stock_codes("301", 0, 999))

    elif index_code == "000688":  # 科创板
        a_stocks = _get_all_a_stocks_from_api()
        if a_stocks:
            a_stocks = [s for s in a_stocks if s.startswith(('688', '689'))]
        else:
            a_stocks = (generate_stock_codes("688", 1, 999)
                        + generate_stock_codes("689", 0, 999))

    elif index_code == "399001":  # 深市全部
        a_stocks = _get_all_a_stocks_from_api()
        if a_stocks:
            a_stocks = [s for s in a_stocks if s.startswith(('000', '001', '002', '003', '300', '301'))]
        else:
            a_stocks = (generate_stock_codes("000", 1, 999)
                        + generate_stock_codes("002", 0, 999)
                        + generate_stock_codes("300", 0, 999))

    elif index_code == "000905":  # 中证500 - 用全量后过滤中等市值
        a_stocks = _get_all_a_stocks_from_api()
        if not a_stocks:
            a_stocks = (generate_stock_codes("000", 500, 999)
                        + generate_stock_codes("600", 500, 799))

    elif index_code == "000300":  # 沪深300（兼容旧代码）
        a_stocks = _get_all_a_stocks_from_api()
        if not a_stocks:
            a_stocks = (generate_stock_codes("000", 1, 200)
                        + generate_stock_codes("600", 0, 300))

    else:
        print(f"不支持的指数代码: {index_code}")
        a_stocks = ["000001", "000002", "600000", "600016"]

    # 去重
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
