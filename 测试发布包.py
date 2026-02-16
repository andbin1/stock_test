"""
测试发布包 - 模拟用户首次使用体验
"""
import subprocess
import sys
import time
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def test_dependency_installation():
    """测试依赖安装"""
    print_header("测试1: 依赖安装")

    requirements_file = "requirements_release.txt"

    if not Path(requirements_file).exists():
        print(f"❌ 找不到 {requirements_file}")
        return False

    print(f"✓ 找到 {requirements_file}")
    print("\n模拟安装命令:")
    print(f"  pip install -r {requirements_file}")

    # 检查主要依赖
    required_packages = ["flask", "pandas", "numpy"]
    all_installed = True

    print("\n检查关键依赖:")
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} 已安装")
        except ImportError:
            print(f"  ✗ {package} 未安装")
            all_installed = False

    return all_installed

def test_app_import():
    """测试应用导入"""
    print_header("测试2: 应用模块导入")

    modules_to_test = [
        ("config", "配置模块"),
        ("strategy", "策略模块"),
        ("backtest_engine", "回测引擎"),
        ("data_manager", "数据管理模块"),
        ("data_fetcher", "数据获取模块"),
    ]

    all_passed = True
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {display_name} ({module_name}.py)")
        except Exception as e:
            print(f"✗ {display_name} - 错误: {str(e)}")
            all_passed = False

    return all_passed

def test_config_loading():
    """测试配置加载"""
    print_header("测试3: 配置加载")

    try:
        from config import START_DATE, END_DATE, STRATEGY_PARAMS, SECTORS
        print("✓ 基础配置加载成功")
        print(f"  - 开始日期: {START_DATE}")
        print(f"  - 结束日期: {END_DATE}")
        print(f"  - 策略参数: 已加载")
        print(f"  - 板块配置: {len(SECTORS)} 个板块")
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

def test_strategy_creation():
    """测试策略创建"""
    print_header("测试4: 策略实例化")

    try:
        from strategy import VolumeBreakoutStrategy
        from config import STRATEGY_PARAMS

        strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
        print("✓ 策略实例化成功")
        print(f"  策略类型: {strategy.__class__.__name__}")
        return True
    except Exception as e:
        print(f"✗ 策略创建失败: {e}")
        return False

def test_data_manager():
    """测试数据管理器"""
    print_header("测试5: 数据管理器")

    try:
        from data_manager import DataManager

        manager = DataManager()
        print("✓ 数据管理器初始化成功")

        # 检查数据库
        if manager.db_file.exists():
            print(f"✓ 数据库文件存在: {manager.db_file}")
        else:
            print(f"⚠️  数据库文件不存在（首次运行正常）")

        return True
    except Exception as e:
        print(f"✗ 数据管理器测试失败: {e}")
        return False

def test_flask_app():
    """测试 Flask 应用"""
    print_header("测试6: Flask 应用")

    try:
        from app_with_cache import app

        print("✓ Flask 应用加载成功")

        # 测试路由
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ 主页路由正常")
            else:
                print(f"⚠️  主页返回状态码: {response.status_code}")

        return True
    except Exception as e:
        print(f"✗ Flask 应用测试失败: {e}")
        return False

def test_template_files():
    """测试模板文件"""
    print_header("测试7: 模板文件")

    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("✗ templates/ 目录不存在")
        return False

    required_templates = ["index_with_cache.html"]
    all_exist = True

    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            size_kb = template_path.stat().st_size / 1024
            print(f"✓ {template} ({size_kb:.1f} KB)")
        else:
            print(f"✗ {template} 不存在")
            all_exist = False

    return all_exist

def main():
    """主测试流程"""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       量化回测系统 - 发布包测试工具                  ║")
    print("╚═══════════════════════════════════════════════════════╝")

    print(f"\n测试环境:")
    print(f"  Python 版本: {sys.version}")
    print(f"  工作目录: {Path.cwd()}")

    # 运行所有测试
    tests = [
        ("依赖安装", test_dependency_installation),
        ("模块导入", test_app_import),
        ("配置加载", test_config_loading),
        ("策略创建", test_strategy_creation),
        ("数据管理", test_data_manager),
        ("Flask应用", test_flask_app),
        ("模板文件", test_template_files),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n⚠️  测试 '{test_name}' 异常: {e}")
            results.append((test_name, False))

    # 统计结果
    print_header("测试总结")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"测试通过: {passed}/{total}\n")

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")

    print("\n" + "="*60)

    if passed == total:
        print("\n🎉 所有测试通过！发布包可以正常使用。")
        print("\n建议:")
        print("  1. 手动启动应用测试完整流程")
        print("  2. 测试数据获取功能")
        print("  3. 测试回测功能")
        print("  4. 测试 Excel 导出")
    else:
        print("\n⚠️  部分测试未通过，建议检查后再发布。")

    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

    input("\n按任意键退出...")
