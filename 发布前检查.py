"""
发布前检查工具 - 验证发布包完整性
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("🐍 检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (需要 3.8+)")
        return False

def check_required_files():
    """检查必需文件是否存在"""
    print("\n📄 检查核心文件...")

    required_files = [
        "app_with_cache.py",
        "backtest_engine.py",
        "strategy.py",
        "data_manager.py",
        "data_fetcher.py",
        "config.py",
        "requirements_release.txt",
        "启动应用.bat",
    ]

    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (缺失)")
            missing.append(file)

    return len(missing) == 0, missing

def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")

    required_packages = [
        ("flask", "Flask"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
    ]

    missing = []
    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} (未安装)")
            missing.append(display_name)

    return len(missing) == 0, missing

def check_syntax():
    """检查 Python 文件语法"""
    print("\n🔍 检查 Python 文件语法...")

    py_files = [
        "app_with_cache.py",
        "backtest_engine.py",
        "strategy.py",
        "data_manager.py",
        "data_fetcher.py",
    ]

    errors = []
    for file in py_files:
        if not Path(file).exists():
            continue

        try:
            import py_compile
            py_compile.compile(file, doraise=True)
            print(f"  ✓ {file}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ {file} (语法错误)")
            errors.append((file, str(e)))

    return len(errors) == 0, errors

def check_templates():
    """检查模板文件"""
    print("\n🎨 检查模板文件...")

    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("  ✗ templates/ 目录不存在")
        return False, ["templates/ 目录"]

    required_templates = ["index_with_cache.html"]
    missing = []

    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} (缺失)")
            missing.append(template)

    return len(missing) == 0, missing

def check_import_modules():
    """测试导入核心模块"""
    print("\n⚙️  测试导入核心模块...")

    modules = [
        ("config", "配置模块"),
        ("strategy", "策略模块"),
        ("backtest_engine", "回测引擎"),
        ("data_manager", "数据管理"),
    ]

    errors = []
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except Exception as e:
            print(f"  ✗ {display_name}: {str(e)}")
            errors.append((module_name, str(e)))

    return len(errors) == 0, errors

def main():
    """主检查流程"""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       量化回测系统 - 发布前检查工具                  ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()

    all_passed = True
    issues = []

    # 1. Python 版本
    if not check_python_version():
        all_passed = False
        issues.append("Python 版本过低")

    # 2. 必需文件
    passed, missing = check_required_files()
    if not passed:
        all_passed = False
        issues.append(f"缺失文件: {', '.join(missing)}")

    # 3. 依赖包
    passed, missing = check_dependencies()
    if not passed:
        all_passed = False
        issues.append(f"缺失依赖: {', '.join(missing)}")

    # 4. 语法检查
    passed, errors = check_syntax()
    if not passed:
        all_passed = False
        issues.append(f"语法错误: {len(errors)} 个文件")

    # 5. 模板文件
    passed, missing = check_templates()
    if not passed:
        all_passed = False
        issues.append(f"缺失模板: {', '.join(missing)}")

    # 6. 模块导入
    passed, errors = check_import_modules()
    if not passed:
        all_passed = False
        issues.append(f"导入错误: {len(errors)} 个模块")

    # 总结
    print("\n" + "="*60)
    if all_passed:
        print("\n✅ 所有检查通过！可以发布。")
        print("\n下一步：")
        print("  1. 运行 python 创建发布包.py")
        print("  2. 测试生成的发布包")
        print("  3. 分享给用户")
    else:
        print("\n❌ 检查未通过，发现以下问题：")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n请修复这些问题后再发布。")

    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 检查过程出错: {e}")
        import traceback
        traceback.print_exc()

    input("\n按任意键退出...")
