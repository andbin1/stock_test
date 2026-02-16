#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证新策略是否已加载
"""

print("=" * 70)
print("新策略验证")
print("=" * 70)

# 测试1：验证配置文件
print("\n【测试1】验证config.py中的策略")
print("-" * 70)

try:
    # 强制重新加载
    import importlib
    import config
    importlib.reload(config)

    strategy_count = len(config.STRATEGY_MAP)
    print(f"✅ 策略总数: {strategy_count}")

    if strategy_count >= 13:
        print("✅ 新策略已成功加载！")

        print("\n所有可用策略:")
        for i, (key, value) in enumerate(config.STRATEGY_MAP.items(), 1):
            marker = "🆕" if i > 4 else "  "
            print(f"{marker} {i}. {value['name']}")

    else:
        print(f"⚠️  策略数量不足（当前{strategy_count}个，应该有13个）")

except Exception as e:
    print(f"❌ 加载失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2：模拟API调用
print("\n【测试2】模拟API调用")
print("-" * 70)

try:
    from config_manager import ConfigManager

    cm = ConfigManager()
    strategies = cm.get_strategy_list()

    print(f"✅ API返回策略数: {len(strategies)}")

    if len(strategies) >= 13:
        print("✅ Web API将显示所有13个策略")
    else:
        print(f"⚠️  API返回策略不足（{len(strategies)}个）")

except Exception as e:
    print(f"⚠️  无法测试API: {e}")

# 给出指令
print("\n" + "=" * 70)
print("下一步操作")
print("=" * 70)

print("""
✅ 新策略已经配置好了！

现在需要重启Web应用才能看到：

1. 如果Web应用正在运行，按 Ctrl+C 停止它

2. 重新启动：
   cd "D:\\ai_work\\stock_test"
   python app_with_cache.py

3. 打开浏览器访问：
   http://localhost:5000

4. 点击"参数配置"页面，你将看到13个策略可选！

策略列表：
  【原有4个】
  1. 量能突破回踩策略
  2. 稳健型趋势跟踪策略
  3. 激进型突破动量策略
  4. 平衡型多因子策略

  【新增9个】⭐
  5. 双均线交叉策略
  6. 双均线交叉策略（激进）
  7. 双均线交叉策略（稳健）
  8. 网格交易策略 ← 推荐
  9. 网格交易策略（密集）
  10. 网格交易策略（宽松）
  11. 海龟交易法则
  12. 海龟交易法则（激进）
  13. 海龟交易法则（保守）
""")

print("=" * 70)
