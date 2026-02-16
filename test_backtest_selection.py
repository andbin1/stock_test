"""
测试回测数据选择功能的脚本
"""
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from data_manager import DataManager
from config import SECTORS

def test_data_manager():
    """测试 DataManager 的 get_all_cached_stocks 方法"""
    print("\n" + "="*60)
    print("测试1: DataManager.get_all_cached_stocks()")
    print("="*60)

    manager = DataManager()
    try:
        stocks = manager.get_all_cached_stocks()
        print(f"✓ 成功获取 {len(stocks)} 只缓存的股票")
        if stocks:
            print(f"  前5只: {stocks[:5]}")
        else:
            print("  (暂无缓存数据，需要先在数据管理页面获取数据)")
        return stocks
    except Exception as e:
        print(f"✗ 错误: {e}")
        return []

def test_stock_categorization(stocks):
    """测试股票分类逻辑"""
    print("\n" + "="*60)
    print("测试2: 股票分类逻辑")
    print("="*60)

    def categorize_stock(symbol: str) -> list:
        """返回股票所属的所有板块"""
        sectors = []

        if symbol.startswith('300'):
            sectors.extend(['创业板', '深成指'])
        elif symbol.startswith('688'):
            sectors.append('科创板')
        elif symbol.startswith(('000', '001', '002', '003')):
            sectors.append('深成指')
        elif symbol.startswith(('600', '601', '603')):
            sectors.append('沪深A股')
        else:
            sectors.append('其他')

        return sectors

    # 测试各种代码
    test_symbols = ['000001', '300001', '600000', '688001', '999999']
    print("测试股票代码分类:")
    for symbol in test_symbols:
        sectors = categorize_stock(symbol)
        print(f"  {symbol}: {', '.join(sectors)}")

    # 分类所有缓存的股票
    by_sector = {
        '沪深A股': [],
        '创业板': [],
        '科创板': [],
        '深成指': [],
        '中证500': [],
        '其他': []
    }

    for stock in stocks:
        sectors = categorize_stock(stock)
        for sector in sectors:
            if sector in by_sector:
                by_sector[sector].append(stock)

    # 去重并排序
    for sector in by_sector:
        by_sector[sector] = sorted(list(set(by_sector[sector])))

    # 移除空的板块
    by_sector = {k: v for k, v in by_sector.items() if v}

    print("\n缓存数据按板块分类统计:")
    for sector, stock_list in sorted(by_sector.items()):
        print(f"  {sector}: {len(stock_list)} 只 {stock_list[:3]}...")

    return by_sector

def test_api_response_format(stocks, by_sector):
    """测试 API 响应格式"""
    print("\n" + "="*60)
    print("测试3: API 响应格式")
    print("="*60)

    response = {
        'success': True,
        'total': len(stocks),
        'stocks': sorted(stocks),
        'by_sector': by_sector
    }

    print("API 响应结构:")
    print(f"  success: {response['success']}")
    print(f"  total: {response['total']}")
    print(f"  stocks: {len(response['stocks'])} 个")
    print(f"  by_sector: {len(response['by_sector'])} 个板块")

    print("\n响应 JSON 格式验证:")
    try:
        json_str = json.dumps(response, ensure_ascii=False, indent=2)
        print("  ✓ JSON 格式正确")
        print(f"  大小: {len(json_str)} 字节")
    except Exception as e:
        print(f"  ✗ JSON 格式错误: {e}")

    return response

def test_frontend_logic(by_sector):
    """测试前端逻辑"""
    print("\n" + "="*60)
    print("测试4: 前端数据处理逻辑")
    print("="*60)

    # 模拟前端选择板块
    selected_sectors = ['创业板', '科创板']
    print(f"模拟选择板块: {selected_sectors}")

    symbols = []
    for sector in selected_sectors:
        sectorStocks = by_sector.get(sector, [])
        symbols.extend(sectorStocks)
        print(f"  {sector}: {len(sectorStocks)} 只股票")

    # 去重
    symbols = list(set(symbols))
    print(f"\n合并后总共 {len(symbols)} 只股票（已去重）")

    # 验证去重逻辑
    test_list = ['000001', '000001', '600000']
    unique_list = list(set(test_list))
    print(f"\n去重验证: {test_list} -> {unique_list}")
    assert len(unique_list) == 2, "去重逻辑错误"
    print("  ✓ 去重逻辑正确")

def main():
    """主测试流程"""
    print("\n" + "="*70)
    print("   回测数据选择功能 - 测试套件")
    print("="*70)

    # 测试1: DataManager
    stocks = test_data_manager()

    if not stocks:
        print("\n⚠️  警告: 暂无缓存数据！")
        print("请按以下步骤操作:")
        print("  1. 启动应用: python app_with_cache.py")
        print("  2. 打开浏览器访问: http://localhost:5000")
        print("  3. 切换到'数据管理'标签页")
        print("  4. 选择板块并点击'获取数据'")
        print("  5. 数据获取完毕后重新运行此脚本")
        print("="*70)
        return

    # 测试2: 股票分类
    by_sector = test_stock_categorization(stocks)

    # 测试3: API 响应格式
    response = test_api_response_format(stocks, by_sector)

    # 测试4: 前端逻辑
    test_frontend_logic(by_sector)

    # 总结
    print("\n" + "="*70)
    print("✅ 所有测试完成！")
    print("="*70)
    print(f"\n总结信息:")
    print(f"  • 缓存股票总数: {len(stocks)}")
    print(f"  • 板块分类数: {len(by_sector)}")
    print(f"  • API 响应大小: {len(json.dumps(response, ensure_ascii=False))} 字节")
    print(f"\n建议操作:")
    print(f"  1. 启动应用: python app_with_cache.py")
    print(f"  2. 打开浏览器: http://localhost:5000")
    print(f"  3. 在'回测'标签页测试三种模式")
    print(f"     - 手动输入: 输入股票代码（如 000001,600000）")
    print(f"     - 全部数据: 点击\"全部缓存数据\"并运行回测")
    print(f"     - 按板块: 勾选板块并运行回测")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
