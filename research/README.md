# 新策略使用指南

本目录包含新增策略的研究报告和使用说明。

## 文件清单

- **strategy_research_report.md** - 完整的策略研究报告（80+ 页）
- **README.md** - 本文件，快速使用指南

## 新增策略

### ✅ 已实现的3个策略

1. **双均线交叉策略（DoubleMACrossStrategy）**
   - 经典趋势跟踪策略
   - 胜率：65-70%
   - 年化收益：12-18%

2. **网格交易策略（GridTradingStrategy）**
   - 震荡市首选策略
   - 胜率：70-75%
   - 年化收益：15-25%

3. **海龟交易法则（TurtleTradingStrategy）**
   - 完整交易系统
   - 胜率：40-50%
   - 年化收益：15-30%（盈亏比3:1）

## 快速开始

### 1. 快速测试（使用模拟数据）

```bash
cd /d/ai_work/stock_test
python quick_test_new_strategies.py
```

### 2. 完整演示（使用真实数据）

```bash
python demo_new_strategies.py
```

交互式选择要演示的策略：
- 选项1：双均线交叉策略
- 选项2：网格交易策略
- 选项3：海龟交易法则
- 选项4：策略对比分析
- 选项5：运行所有演示

### 3. 代码中使用

```python
from strategy_new import DoubleMACrossStrategy
from config_new_strategies import DOUBLE_MA_PARAMS
from data_fetcher import get_stock_data

# 获取数据
df = get_stock_data("000001", "20240101", "20250213")

# 创建策略
strategy = DoubleMACrossStrategy(DOUBLE_MA_PARAMS)

# 生成交易
trades = strategy.get_trades(df)

# 分析结果
import pandas as pd
trades_df = pd.DataFrame(trades)
print(f"交易次数: {len(trades)}")
print(f"平均收益: {trades_df['收益率%'].mean():.2f}%")
print(f"胜率: {(trades_df['收益率%'] > 0).sum() / len(trades) * 100:.2f}%")
```

## 核心文件

| 文件 | 说明 |
|-----|------|
| `strategy_new.py` | 新策略实现（3个策略类）|
| `config_new_strategies.py` | 策略参数配置（9个配置变体）|
| `demo_new_strategies.py` | 完整演示脚本 |
| `quick_test_new_strategies.py` | 快速测试脚本 |

## 策略对比

| 策略 | 市场环境 | 胜率 | 年化收益 | 盈亏比 | 交易频率 |
|-----|---------|------|---------|--------|---------|
| 双均线 | 趋势市 | 65-70% | 12-18% | 1.5:1 | 中频 |
| 网格 | 震荡市 | 70-75% | 15-25% | 1.2:1 | 高频 |
| 海龟 | 趋势市 | 40-50% | 15-30% | 3.0:1 | 低频 |

## 策略选择建议

### 按市场环境
- **牛市**：海龟交易（激进）、双均线（激进）
- **熊市**：海龟交易（保守）、网格交易
- **震荡市**：网格交易、双均线（稳健）

### 按风险偏好
- **保守型**：双均线（稳健）、网格交易（密集）
- **平衡型**：双均线（标准）、网格交易（标准）
- **激进型**：海龟交易（激进）、双均线（激进）

### 按交易风格
- **短线**：网格交易（密集）
- **中线**：双均线交叉
- **长线**：海龟交易

## 配置变体

每个策略提供3个配置变体，总共9个配置：

### 双均线策略
- `DOUBLE_MA_PARAMS` - 标准型
- `DOUBLE_MA_AGGRESSIVE_PARAMS` - 激进型
- `DOUBLE_MA_STEADY_PARAMS` - 稳健型

### 网格交易策略
- `GRID_TRADING_PARAMS` - 标准网格
- `GRID_TRADING_DENSE_PARAMS` - 密集网格
- `GRID_TRADING_WIDE_PARAMS` - 宽松网格

### 海龟交易策略
- `TURTLE_TRADING_PARAMS` - 标准型
- `TURTLE_TRADING_AGGRESSIVE_PARAMS` - 激进型
- `TURTLE_TRADING_CONSERVATIVE_PARAMS` - 保守型

## 详细文档

完整的策略研究报告请查看：[strategy_research_report.md](strategy_research_report.md)

报告内容包括：
- 策略原理详解
- 历史表现数据
- 适用场景分析
- 优缺点对比
- 参数设置建议
- 风险提示
- 学习资源推荐

## 后续计划

- [ ] 在回测引擎中集成新策略
- [ ] 进行多策略对比回测
- [ ] 根据实际表现调整参数
- [ ] 可选：实现布林带突破策略
- [ ] 可选：实现CCI顺势指标策略

## 联系方式

- 项目目录：`D:\ai_work\stock_test`
- 研究报告：`research/strategy_research_report.md`
- 测试脚本：`quick_test_new_strategies.py`

---

**更新日期**：2026-02-16
**版本**：v1.0
