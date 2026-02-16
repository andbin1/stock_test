#!/bin/bash

echo ""
echo "========================================"
echo "  A股交易策略回测系统"
echo "========================================"
echo ""

# 检查Python
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python"
    echo "请先安装Python 3.7+ 并确保已加入PATH"
    exit 1
fi

echo "正在检查依赖..."
if ! python -c "import akshare" 2>/dev/null; then
    echo ""
    echo "首次运行，正在安装依赖..."
    echo ""
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "选择要运行的程序:"
echo "========================================"
echo "1. 快速测试 (quick_test.py) - 3分钟，5只样本股"
echo "2. 完整回测 (main.py) - 15-30分钟，沪深300+中证500"
echo "3. 参数优化 (param_optimizer.py) - 30-60分钟，找最优参数"
echo "4. 退出"
echo ""
read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "运行快速测试..."
        python quick_test.py
        ;;
    2)
        echo ""
        echo "运行完整回测 (请耐心等待)..."
        python main.py
        ;;
    3)
        echo ""
        echo "运行参数优化 (请耐心等待)..."
        python param_optimizer.py
        ;;
    4)
        exit 0
        ;;
    *)
        echo "输入有误"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "完成！请查看生成的文件"
echo "========================================"
