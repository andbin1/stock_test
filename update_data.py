#!/usr/bin/env python3
"""
手动批量更新缓存股票数据

用法:
  python update_data.py               # 更新所有已缓存的股票
  python update_data.py 000001 600000 # 更新指定股票代码
"""
import sys
from datetime import datetime
from data_manager import DataManager


def main():
    manager = DataManager()

    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
        print(f"手动更新指定股票: {', '.join(symbols)}")
    else:
        symbols = manager.get_all_cached_stocks()
        print(f"更新所有已缓存股票，共 {len(symbols)} 只")

    if not symbols:
        print("没有找到需要更新的股票，请先通过页面获取数据")
        return

    success = 0
    failed = 0
    start_time = datetime.now()

    for i, symbol in enumerate(symbols, 1):
        try:
            result = manager.update_single_stock(symbol)
            if result:
                print(f"  [{i:>4}/{len(symbols)}] ✓ {symbol}")
            else:
                print(f"  [{i:>4}/{len(symbols)}] - {symbol}（无新数据）")
            success += 1
        except Exception as e:
            print(f"  [{i:>4}/{len(symbols)}] ✗ {symbol}: {e}")
            failed += 1

    elapsed = int((datetime.now() - start_time).total_seconds())
    print(f"\n完成: {success} 成功, {failed} 失败, 耗时 {elapsed}s")


if __name__ == "__main__":
    main()
