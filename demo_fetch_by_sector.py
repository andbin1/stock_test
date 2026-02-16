"""
演示脚本：按板块批量获取股票数据

展示如何使用新的板块获取功能
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def print_header(title):
    """打印分隔符"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def get_sectors():
    """获取所有可用板块"""
    print_header("获取所有可用板块")

    try:
        response = requests.get(f"{BASE_URL}/api/sectors")
        result = response.json()

        if result['success']:
            print("✓ 可用板块列表：\n")
            for i, sector in enumerate(result['sectors'], 1):
                print(f"{i}. {sector['name']}")
                print(f"   代码: {sector['key']}")
                print(f"   说明: {sector['description']}\n")
            return [s['key'] for s in result['sectors']]
        else:
            print(f"✗ 错误: {result['error']}")
            return []
    except Exception as e:
        print(f"✗ 网络错误: {e}")
        return []

def fetch_sector_data(sector, start_date="20240101", end_date="20250213"):
    """按板块获取数据"""
    print_header(f"按板块获取数据: {sector}")

    try:
        payload = {
            "sector": sector,
            "start_date": start_date,
            "end_date": end_date
        }

        print(f"请求参数：")
        print(f"  板块: {sector}")
        print(f"  时间范围: {start_date[:4]}-{start_date[4:6]}-{start_date[6:8]} 至 {end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}\n")

        response = requests.post(f"{BASE_URL}/api/cache/batch-fetch-sector", json=payload)
        result = response.json()

        if result['success']:
            print(f"✓ 成功！\n")
            print(f"任务ID: {result['task_id']}")
            print(f"板块: {result['sector']}")
            print(f"股票数: {result['stocks_count']}")
            print(f"首批股票: {', '.join(result['stocks'])}...")
            print(f"\n📝 消息: {result['message']}")
        else:
            print(f"✗ 错误: {result['error']}")
    except Exception as e:
        print(f"✗ 网络错误: {e}")

def get_cache_status():
    """获取缓存状态"""
    print_header("获取缓存状态")

    try:
        response = requests.get(f"{BASE_URL}/api/cache/status")
        result = response.json()

        if result['success']:
            print(f"✓ 缓存信息：\n")
            print(f"总记录数: {result['total_records']} 条")
            print(f"数据库大小: {result['db_size']} MB")
            print(f"数据库位置: {result['db_file']}\n")

            if result['update_logs']:
                print(f"📝 更新日志（前5条）：\n")
                for log in result['update_logs'][:5]:
                    print(f"  {log['symbol']}: {log['record_count']} 条数据")
                    print(f"    最后数据: {log['last_date']}")
                    print(f"    更新时间: {log['last_update']}\n")
        else:
            print(f"✗ 错误: {result['error']}")
    except Exception as e:
        print(f"✗ 网络错误: {e}")

def main():
    """主函数"""
    print("\n")
    print("  " + "╔" + "═"*66 + "╗")
    print("  " + "║" + " "*10 + "📥 按板块批量获取数据 - 演示脚本" + " "*22 + "║")
    print("  " + "╚" + "═"*66 + "╝")

    # 第1步：获取所有可用板块
    print("\n【第1步】获取所有可用板块\n")
    sectors = get_sectors()

    if not sectors:
        print("✗ 无法获取板块列表，请确保Flask应用已启动在 http://localhost:5000")
        return

    # 第2步：演示获取不同板块的数据
    print("\n【第2步】按板块获取数据\n")

    # 示例：获取创业板数据
    print("🎯 演示1：获取创业板数据")
    fetch_sector_data("创业板")

    input("\n按Enter继续下一个演示...")

    # 示例：获取科创板数据
    print("\n🎯 演示2：获取科创板数据")
    fetch_sector_data("科创板")

    input("\n按Enter继续查看缓存状态...")

    # 第3步：查看缓存状态
    print("\n【第3步】查看缓存状态\n")
    get_cache_status()

    # 完成
    print_header("演示完成")
    print("✅ 所有演示已完成！\n")
    print("后续步骤：")
    print("1. 打开浏览器访问 http://localhost:5000")
    print("2. 进入\"📊 数据管理\"标签页")
    print("3. 查看已获取的板块数据")
    print("4. 切换到\"🔄 回测\"标签进行策略回测")
    print("5. 使用\"⚙️ 参数配置\"调整策略参数\n")

if __name__ == "__main__":
    print("确保Flask应用已启动: python app_with_cache.py\n")
    input("按Enter开始演示...")
    main()
