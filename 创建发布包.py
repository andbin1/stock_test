"""
创建发布包 - 自动打包脚本
将项目打包为可分发的版本
"""
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# 版本信息
VERSION = "v2.1"
RELEASE_NAME = f"stock_test_{VERSION}_release"

# 需要包含的文件
INCLUDE_FILES = [
    # 核心程序
    "app_with_cache.py",
    "backtest_engine.py",
    "strategy.py",
    "indicators.py",
    "data_manager.py",
    "data_fetcher.py",
    "config.py",
    "config_manager.py",
    "export_to_excel.py",
    "trading_cost.py",
    "demo_test_debug.py",

    # 启动和配置
    "启动应用.bat",
    "安装依赖.bat",
    "requirements_release.txt",

    # 文档
    "README_发布版.md",
    "用户使用手册.md",
    "发布清单.txt",
]

# 需要包含的目录
INCLUDE_DIRS = [
    "templates",
]

# 可选文件（如果存在才包含）
OPTIONAL_FILES = [
    "strategy_new.py",
    "config_new_strategies.py",
    "STRATEGY_GUIDE.md",
]

def create_release_package():
    """创建发布包"""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       量化回测系统 - 发布包创建工具                  ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()

    # 当前目录
    current_dir = Path.cwd()

    # 创建发布目录
    release_dir = current_dir / RELEASE_NAME
    if release_dir.exists():
        print(f"⚠️  发现已存在的发布目录: {release_dir}")
        response = input("是否删除并重新创建？(Y/N): ")
        if response.upper() == 'Y':
            shutil.rmtree(release_dir)
            print("✓ 已删除旧版本")
        else:
            print("❌ 取消操作")
            return

    release_dir.mkdir(exist_ok=True)
    print(f"✓ 创建发布目录: {release_dir}")
    print()

    # 复制文件
    print("📦 开始复制文件...")
    copied_count = 0
    missing_files = []

    for file in INCLUDE_FILES:
        src = current_dir / file
        if src.exists():
            dst = release_dir / file
            shutil.copy2(src, dst)
            print(f"  ✓ {file}")
            copied_count += 1
        else:
            missing_files.append(file)
            print(f"  ✗ {file} (未找到)")

    # 复制可选文件
    for file in OPTIONAL_FILES:
        src = current_dir / file
        if src.exists():
            dst = release_dir / file
            shutil.copy2(src, dst)
            print(f"  ✓ {file} (可选)")
            copied_count += 1

    print()

    # 复制目录
    print("📂 复制目录...")
    for dir_name in INCLUDE_DIRS:
        src_dir = current_dir / dir_name
        if src_dir.exists():
            dst_dir = release_dir / dir_name
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (未找到)")

    print()

    # 创建空目录（运行时需要）
    print("📁 创建必要目录...")
    for dir_name in ["data_cache", "backtest_results", "logs"]:
        (release_dir / dir_name).mkdir(exist_ok=True)
        # 创建 .gitkeep 以保留目录
        (release_dir / dir_name / ".gitkeep").touch()
        print(f"  ✓ {dir_name}/")

    print()

    # 创建版本信息文件
    version_info = f"""量化回测系统 {VERSION}
发布日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python 版本要求: 3.8+

包含文件: {copied_count} 个
"""
    (release_dir / "VERSION.txt").write_text(version_info, encoding='utf-8')
    print("✓ 创建版本信息文件")
    print()

    # 显示统计信息
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ 发布包创建完成！")
    print(f"📍 位置: {release_dir}")
    print(f"📊 文件数: {copied_count}")
    if missing_files:
        print(f"⚠️  缺失文件: {len(missing_files)}")
        for f in missing_files:
            print(f"    - {f}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 询问是否压缩
    response = input("是否创建 ZIP 压缩包？(Y/N): ")
    if response.upper() == 'Y':
        create_zip(release_dir)

def create_zip(release_dir: Path):
    """创建 ZIP 压缩包"""
    print()
    print("📦 创建 ZIP 压缩包...")

    zip_path = release_dir.parent / f"{release_dir.name}.zip"

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            # 排除 __pycache__
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(release_dir.parent)
                zipf.write(file_path, arcname)
                print(f"  压缩: {arcname}")

    # 获取压缩包大小
    size_mb = zip_path.stat().st_size / (1024 * 1024)

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ ZIP 压缩包创建完成！")
    print(f"📍 位置: {zip_path}")
    print(f"📊 大小: {size_mb:.2f} MB")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("📤 现在可以分享这个 ZIP 文件给其他用户了！")

if __name__ == "__main__":
    try:
        create_release_package()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    input("\n按任意键退出...")
