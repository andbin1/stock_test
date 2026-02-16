"""
测试新的API端点
"""
import sys
from pathlib import Path
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入Flask应用
from app_with_cache import app, config_manager, manager
from demo_test_debug import generate_better_mock_data

def test_strategy_apis():
    """测试策略相关的API"""
    print("\n" + "="*60)
    print("测试策略API端点")
    print("="*60)

    with app.test_client() as client:
        # 1. 测试获取策略列表
        print("\n1. GET /api/strategies - 获取策略列表")
        response = client.get('/api/strategies')
        result = json.loads(response.data)
        print(f"   状态码: {response.status_code}")
        print(f"   成功: {result['success']}")
        print(f"   策略数: {len(result.get('strategies', []))}")
        print(f"   当前策略: {result.get('current_strategy')}")
        if result['success']:
            for strategy in result['strategies']:
                print(f"     - {strategy['name']} ({strategy['key']})")

        # 2. 测试获取当前策略
        print("\n2. GET /api/strategies/current - 获取当前策略配置")
        response = client.get('/api/strategies/current')
        result = json.loads(response.data)
        print(f"   状态码: {response.status_code}")
        print(f"   成功: {result['success']}")
        if result['success']:
            print(f"   当前策略: {result['strategy']}")
            print(f"   参数数: {len(result.get('params', {}))}")

        # 3. 测试切换策略
        print("\n3. POST /api/strategies/current - 切换到稳健策略")
        response = client.post('/api/strategies/current',
                             json={'strategy': 'steady_trend'},
                             content_type='application/json')
        result = json.loads(response.data)
        print(f"   状态码: {response.status_code}")
        print(f"   成功: {result['success']}")
        print(f"   消息: {result.get('message', '')}")

        # 4. 测试获取特定策略参数
        print("\n4. GET /api/strategies/aggressive_momentum/params - 获取激进策略参数")
        response = client.get('/api/strategies/aggressive_momentum/params')
        result = json.loads(response.data)
        print(f"   状态码: {response.status_code}")
        print(f"   成功: {result['success']}")
        if result['success']:
            print(f"   策略: {result['strategy']}")
            print(f"   参数数: {len(result.get('params', {}))}")
            # 显示前几个参数
            params = result.get('params', {})
            for i, (key, value) in enumerate(list(params.items())[:5]):
                print(f"     {key}: {value}")

        # 5. 测试回测API（带策略参数）
        print("\n5. POST /api/backtest/cache - 运行回测（带策略选择）")

        # 先生成模拟数据用于缓存
        print("   准备测试数据...")
        mock_df = generate_better_mock_data('000001', days=250)
        manager.save_data_to_cache('000001', mock_df)

        response = client.post('/api/backtest/cache',
                             json={
                                 'symbols': ['000001'],
                                 'strategy': 'balanced_multi_factor',
                                 'params': None
                             },
                             content_type='application/json')
        result = json.loads(response.data)
        print(f"   状态码: {response.status_code}")
        print(f"   成功: {result['success']}")
        if result['success']:
            print(f"   使用策略: {result.get('strategy_name', '')}")
            print(f"   测试股票: {result.get('stocks_tested', 0)}")
            print(f"   总交易数: {result.get('total_trades', 0)}")
            print(f"   总收益: {result.get('total_return', 0):.2f}%")
            print(f"   平均收益: {result.get('avg_return', 0):.2f}%")
            print(f"   胜率: {result.get('win_rate', 0):.1f}%")
        else:
            print(f"   错误: {result.get('error', '')}")

        # 6. 测试使用不同策略回测
        print("\n6. POST /api/backtest/cache - 使用量能突破策略回测")
        response = client.post('/api/backtest/cache',
                             json={
                                 'symbols': ['000001'],
                                 'strategy': 'volume_breakout',
                                 'params': None
                             },
                             content_type='application/json')
        result = json.loads(response.data)
        print(f"   状态码: {response.status_code}")
        print(f"   成功: {result['success']}")
        if result['success']:
            print(f"   使用策略: {result.get('strategy_name', '')}")
            print(f"   总交易数: {result.get('total_trades', 0)}")
            print(f"   总收益: {result.get('total_return', 0):.2f}%")
            print(f"   胜率: {result.get('win_rate', 0):.1f}%")


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("多策略量化回测系统 - API 测试")
    print("="*70)

    try:
        test_strategy_apis()
        print("\n" + "="*70)
        print("✓ 所有API测试完成")
        print("="*70)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
