#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试交易参数配置UI功能
- 验证HTML中的配置面板元素
- 测试JavaScript对象和函数
- 测试API端点集成
"""

import json
import re
from pathlib import Path

def test_html_structure():
    """测试HTML结构中是否包含所有必需的元素"""
    html_path = Path('D:\\ai_work\\stock_test\\templates\\index_with_cache.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        '交易配置面板': 'trading-settings-section' in content,
        '初始资金输入框': 'id="initialCapital"' in content,
        '交易占比下拉框': 'id="positionRatioSelect"' in content,
        '手续费输入框': 'id="commissionRate"' in content,
        '滑点输入框': 'id="slippage"' in content,
        '配置预览区域': 'config-preview' in content,
        '保存配置按钮': 'id="saveSettingsBtn"' in content,
        '配置面板CSS样式': 'trading-settings-section' in content,
    }

    print("=" * 60)
    print("HTML结构验证")
    print("=" * 60)

    for name, check in checks.items():
        status = "✓" if check else "✗"
        print(f"{status} {name}")

    return all(checks.values())


def test_javascript_functions():
    """测试JavaScript中是否包含所有必需的函数"""
    html_path = Path('D:\\ai_work\\stock_test\\templates\\index_with_cache.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取script部分
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("✗ 未找到script部分")
        return False

    script = script_match.group(1)

    checks = {
        'TradingSettingsManager对象': 'const TradingSettingsManager' in script,
        'init方法': 'init: function()' in script,
        'loadSettings方法': 'loadSettings: async function()' in script,
        'getFormValues方法': 'getFormValues: function()' in script,
        'validate方法': 'validate: function()' in script,
        'updatePreview方法': 'updatePreview: function()' in script,
        'saveSettings方法': 'saveSettings: async function()' in script,
        'attachEventListeners方法': 'attachEventListeners: function()' in script,
        '初始化调用': 'TradingSettingsManager.init()' in script,
    }

    print("\n" + "=" * 60)
    print("JavaScript函数验证")
    print("=" * 60)

    for name, check in checks.items():
        status = "✓" if check else "✗"
        print(f"{status} {name}")

    return all(checks.values())


def test_api_integration():
    """测试JavaScript中是否正确调用API"""
    html_path = Path('D:\\ai_work\\stock_test\\templates\\index_with_cache.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'GET配置API调用': '/api/backtest/settings' in content,
        '回测时传递配置参数': 'initial_capital' in content and 'tradingSettings' in content,
        '显示配置信息': 'resultInitialCapital' in content,
    }

    print("\n" + "=" * 60)
    print("API集成验证")
    print("=" * 60)

    for name, check in checks.items():
        status = "✓" if check else "✗"
        print(f"{status} {name}")

    return all(checks.values())


def test_css_styles():
    """测试CSS样式是否完整"""
    html_path = Path('D:\\ai_work\\stock_test\\templates\\index_with_cache.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取style部分
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if not style_match:
        print("✗ 未找到style部分")
        return False

    style = style_match.group(1)

    checks = {
        '.trading-settings-section样式': '.trading-settings-section' in style,
        '.input-wrapper样式': '.input-wrapper' in style,
        '.input-hint样式': '.input-hint' in style,
        '.config-preview样式': '.config-preview' in style,
        '.preview-item样式': '.preview-item' in style,
        '.preview-label样式': '.preview-label' in style,
        '.preview-value样式': '.preview-value' in style,
        '响应式设计': '@media' in style,
    }

    print("\n" + "=" * 60)
    print("CSS样式验证")
    print("=" * 60)

    for name, check in checks.items():
        status = "✓" if check else "✗"
        print(f"{status} {name}")

    return all(checks.values())


def test_backend_api():
    """测试后端API端点是否存在"""
    app_path = Path('D:\\ai_work\\stock_test\\app_with_cache.py')
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'GET /api/backtest/settings': "@app.route('/api/backtest/settings', methods=['GET'])" in content,
        'POST /api/backtest/settings': "@app.route('/api/backtest/settings', methods=['POST'])" in content,
        '参数验证函数': 'validate_trading_settings' in content,
    }

    print("\n" + "=" * 60)
    print("后端API验证")
    print("=" * 60)

    for name, check in checks.items():
        status = "✓" if check else "✗"
        print(f"{status} {name}")

    return all(checks.values())


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "交易参数配置UI测试" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")

    results = {
        'HTML结构': test_html_structure(),
        'JavaScript函数': test_javascript_functions(),
        'API集成': test_api_integration(),
        'CSS样式': test_css_styles(),
        '后端API': test_backend_api(),
    }

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！前端UI已完整实现。")
    else:
        print("✗ 部分测试失败，请检查实现。")
    print("=" * 60 + "\n")

    return all_passed


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
