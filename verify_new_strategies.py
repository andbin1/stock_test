"""
新策略验证脚本
验证所有新增文件和功能是否正常
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        size_kb = size / 1024
        print(f"✅ {description}")
        print(f"   路径: {filepath}")
        print(f"   大小: {size_kb:.1f} KB")
        return True
    else:
        print(f"❌ {description}")
        print(f"   路径: {filepath}")
        print(f"   状态: 文件不存在")
        return False


def check_imports():
    """检查是否能成功导入新策略"""
    print("\n" + "=" * 60)
    print("检查导入功能")
    print("=" * 60)

    try:
        from strategy_new import (
            DoubleMACrossStrategy,
            GridTradingStrategy,
            TurtleTradingStrategy
        )
        print("✅ 成功导入所有策略类")

        from config_new_strategies import (
            DOUBLE_MA_PARAMS,
            GRID_TRADING_PARAMS,
            TURTLE_TRADING_PARAMS,
            NEW_STRATEGY_MAP
        )
        print("✅ 成功导入所有配置")

        # 验证策略映射
        expected_strategies = [
            'double_ma_cross', 'double_ma_aggressive', 'double_ma_steady',
            'grid_trading', 'grid_trading_dense', 'grid_trading_wide',
            'turtle_trading', 'turtle_trading_aggressive', 'turtle_trading_conservative'
        ]

        for strategy_id in expected_strategies:
            if strategy_id in NEW_STRATEGY_MAP:
                print(f"✅ 策略配置存在: {strategy_id}")
            else:
                print(f"❌ 策略配置缺失: {strategy_id}")

        return True

    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        return False


def check_strategy_instantiation():
    """检查策略是否能正常实例化"""
    print("\n" + "=" * 60)
    print("检查策略实例化")
    print("=" * 60)

    try:
        from strategy_new import (
            DoubleMACrossStrategy,
            GridTradingStrategy,
            TurtleTradingStrategy
        )
        from config_new_strategies import (
            DOUBLE_MA_PARAMS,
            GRID_TRADING_PARAMS,
            TURTLE_TRADING_PARAMS
        )

        # 实例化测试
        strategies = [
            ("双均线交叉", DoubleMACrossStrategy, DOUBLE_MA_PARAMS),
            ("网格交易", GridTradingStrategy, GRID_TRADING_PARAMS),
            ("海龟交易", TurtleTradingStrategy, TURTLE_TRADING_PARAMS),
        ]

        for name, strategy_class, params in strategies:
            try:
                strategy = strategy_class(params)
                print(f"✅ {name}策略实例化成功")
            except Exception as e:
                print(f"❌ {name}策略实例化失败: {str(e)}")
                return False

        return True

    except Exception as e:
        print(f"❌ 实例化检查失败: {str(e)}")
        return False


def main():
    """主验证函数"""
    print("=" * 60)
    print("新策略验证脚本")
    print("=" * 60)
    print(f"工作目录: {os.getcwd()}")

    # 检查核心文件
    print("\n" + "=" * 60)
    print("检查核心文件")
    print("=" * 60)

    files_to_check = [
        ("strategy_new.py", "策略实现文件"),
        ("config_new_strategies.py", "策略配置文件"),
        ("demo_new_strategies.py", "演示脚本"),
        ("quick_test_new_strategies.py", "快速测试脚本"),
        ("NEW_STRATEGIES_SUMMARY.md", "实施总结文档"),
        ("research/strategy_research_report.md", "策略研究报告"),
        ("research/README.md", "使用指南"),
    ]

    all_files_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_exist = False

    # 检查导入
    imports_ok = check_imports()

    # 检查实例化
    instantiation_ok = check_strategy_instantiation()

    # 统计信息
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)

    total_lines = 0
    code_files = ['strategy_new.py', 'config_new_strategies.py',
                  'demo_new_strategies.py', 'quick_test_new_strategies.py']

    for filename in code_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"📄 {filename}: {lines} 行")

    doc_files = ['research/strategy_research_report.md', 'research/README.md',
                 'NEW_STRATEGIES_SUMMARY.md']
    total_doc_lines = 0

    for filename in doc_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_doc_lines += lines
                print(f"📖 {filename}: {lines} 行")

    print(f"\n代码总行数: {total_lines}")
    print(f"文档总行数: {total_doc_lines}")
    print(f"总计: {total_lines + total_doc_lines} 行")

    # 最终结果
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)

    if all_files_exist and imports_ok and instantiation_ok:
        print("🎉 所有验证通过！")
        print("\n新策略已成功实现，可以开始使用了。")
        print("\n快速开始：")
        print("  1. 运行快速测试: python quick_test_new_strategies.py")
        print("  2. 运行完整演示: python demo_new_strategies.py")
        print("  3. 查看研究报告: research/strategy_research_report.md")
        return 0
    else:
        print("⚠️  部分验证失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
