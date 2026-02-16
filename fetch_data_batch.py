"""批量获取和缓存数据脚本"""
import sys
from data_manager import DataManager
from data_fetcher import get_index_constituents
from config import START_DATE, END_DATE, INDICES, MAX_STOCKS

def main():
    """批量获取中证500的20只股票数据"""
    manager = DataManager()

    print("="*70)
    print("  批量数据获取工具")
    print("="*70)
    print(f"数据范围: {START_DATE} ~ {END_DATE}")
    print(f"数据来源: efinance / akshare")
    print()

    # 获取指数成分股
    print("📊 获取指数成分股...")
    index_name = "中证500"
    index_code = INDICES.get(index_name, "000905")

    stocks = get_index_constituents(index_code, limit=MAX_STOCKS)

    if not stocks:
        print("❌ 无法获取成分股列表")
        return

    print(f"✓ 获取到 {len(stocks)} 只成分股")
    print(f"  股票列表: {', '.join(stocks[:5])}...")
    print()

    # 批量获取数据
    print("🔄 开始批量获取数据...")
    print("(第一次获取会比较慢，因为需要从网络下载数据)")
    print()

    all_data = manager.batch_fetch_and_cache(stocks, force_refresh=False)

    # 显示结果
    print()
    print("="*70)
    print("  获取完成")
    print("="*70)
    print()

    if all_data:
        print(f"✅ 成功获取 {len(all_data)} 只股票的数据")
        print()
        print("已缓存的股票:")
        for symbol, df in all_data.items():
            print(f"  {symbol}: {len(df)} 条数据 ({df['日期'].min().date()} ~ {df['日期'].max().date()})")

    # 显示缓存状态
    print()
    print("="*70)
    print("  缓存状态")
    print("="*70)
    status = manager.get_cache_status()
    print(f"总记录数: {status['total_records']} 条")
    print(f"数据库大小: {status['db_size']:.2f} MB")
    print(f"数据库位置: {status['db_file']}")
    print()

    # 显示后续操作
    print("="*70)
    print("  后续操作")
    print("="*70)
    print()
    print("✅ 现在可以进行回测：")
    print("   python backtest_with_cache.py")
    print()
    print("📝 其他命令：")
    print("   python data_manager.py status              查看缓存状态")
    print("   python data_manager.py update <symbol>     更新单只股票")
    print("   python data_manager.py export <symbol>     导出为CSV")
    print("   python data_manager.py clear               清空缓存")
    print()

if __name__ == "__main__":
    main()
