# 测试发现的Bug列表

**测试日期**: 2026-02-16
**测试工程师**: AI Test Engineer

---

## Bug #1: 除零保护返回NaN ⚠️ HIGH

**位置**: `backtest_engine.py:124`
**测试用例**: `tests/test_backtest_engine.py::TestEdgeCases::test_divide_by_zero_protection`
**状态**: 未修复

### 问题描述

当所有交易都是亏损（没有盈利交易）时，计算`profit_factor`会返回`NaN`而不是期望的`0`。

### 触发条件

```python
# 所有交易都亏损
trades_df = pd.DataFrame([
    {'收益率%': -5.0},
    {'收益率%': -10.0},
])
```

### 当前代码

```python
# backtest_engine.py:124
'profit_factor': (wins.mean() / abs(losses.mean())) if len(losses) > 0 and losses.mean() != 0 else 0,
```

### 问题原因

- 当`len(wins) == 0`时，`wins`是空数组
- `wins.mean()`返回`np.nan`
- `np.nan / 任何数 = np.nan`
- 导致`profit_factor = NaN`

### 影响范围

- 所有亏损的回测结果中`profit_factor`显示为`NaN`
- 影响报表可读性
- 无法正确比较不同策略的盈亏比
- 后续计算可能因NaN传播导致更多错误

### 修复建议

```python
# 方案1: 先检查wins是否为空
wins = all_returns[all_returns > 0]
losses = all_returns[all_returns <= 0]

avg_profit = wins.mean() if len(wins) > 0 else 0
avg_loss = abs(losses.mean()) if len(losses) > 0 else 0

if avg_loss > 0:
    profit_factor = avg_profit / avg_loss
elif avg_profit > 0:
    profit_factor = 1  # 只有盈利没有亏损
else:
    profit_factor = 0  # 没有交易或全是零收益
```

### 优先级

🔴 **HIGH** - 影响核心回测指标的准确性

---

## Bug #2: 移动止盈可能亏损退出 ⚠️ MEDIUM

**位置**: `strategy.py:222-223` (SteadyTrendStrategy)
**测试用例**: `tests/test_strategy.py::TestSteadyTrendStrategy::test_get_trades_trailing_stop`
**状态**: 不确定是否为Bug（可能是测试假设错误）

### 问题描述

测试期望移动止盈退出时收益率应该为正，但实际可能为负（-6.11%）。

### 触发场景

1. 股票买入后上涨，达到新高价
2. 随后回落超过5%（trailing_stop=0.05）
3. 触发移动止盈卖出
4. 但此时价格可能仍低于买入价，导致亏损

### 示例

```
买入价: 10.00
最高价: 11.00 (上涨10%)
当前价: 9.40 (从最高价回落14.5%，从买入价下跌6%)
触发移动止盈: current_price < 11.00 * 0.95 = 10.45
实际收益率: -6%
```

### 分析

这可能不是Bug，而是策略逻辑的正常行为：
- 移动止盈的目的是保护利润，而不是避免亏损
- 如果价格先涨后跌破买入价，移动止盈会限制亏损在5%以内（相对于最高点）
- 但相对于买入价可能仍是亏损

### 建议

有两种处理方式：

#### 方案1: 修改测试（推荐）

```python
# 移动止盈可能是盈利也可能是亏损
trailing_trades = [t for t in trades if t['状态'] == '移动止盈']
# 只验证移动止盈逻辑被触发
for trade in trailing_trades:
    # 验证是从最高点回落了trailing_stop
    pass
```

#### 方案2: 修改策略

```python
# 添加最低盈利保护
if current_price < position['highest_price'] * (1 - self.trailing_stop):
    if profit_pct > 0:  # 只有盈利时才使用移动止盈
        sell_reason = '移动止盈'
    else:
        # 亏损时使用止损
        if profit_pct <= -self.stop_loss:
            sell_reason = '止损'
```

### 优先级

🟡 **MEDIUM** - 需要确认策略设计意图

---

## 潜在问题（不是Bug，但需要注意）

### Issue #1: 前视偏差风险 ⚠️ HIGH

**位置**: 所有策略的`calculate_signals()`方法

**问题描述**:
某些策略可能使用了未来数据，导致回测结果过于乐观。

**示例**:
```python
# 在第i天使用当天收盘价判断买入
if row['收盘'] < row['MA5']:
    buy_signal = True
```

实际交易中，只能在收盘后才知道当天收盘价，无法在盘中使用当天收盘价做决策。

**建议**:
- 买入信号应基于前一日数据
- 使用`.shift(1)`避免使用当日数据
- 执行价格使用次日开盘价

### Issue #2: 交易成本不完整 ⚠️ MEDIUM

**位置**: 所有策略的`get_trades()`方法

**当前处理**:
```python
profit_pct_after_fee = profit_pct - 0.1  # 手续费往返0.1%
```

**缺失**:
- 印花税 (卖出时0.1%)
- 佣金 (买卖双向，最低5元)
- 滑点 (市价单可能偏离0.1-0.3%)
- 冲击成本 (大单对价格的影响)

**建议**:
```python
# 完整的交易成本计算
commission = max(buy_amount * 0.0003, 5)  # 佣金最低5元
stamp_tax = sell_amount * 0.001  # 印花税
slippage = (buy_price + sell_price) * 0.001  # 滑点
total_cost = commission * 2 + stamp_tax + slippage
```

### Issue #3: 数据质量检查不足 ⚠️ LOW

**位置**: `data_fetcher.py`

**当前处理**:
- 只过滤了收盘价为NaN的行
- 未检查其他异常数据

**建议增加**:
```python
def validate_stock_data(df):
    # 检查价格为正
    assert (df['收盘'] > 0).all(), "收盘价必须为正"
    assert (df['开盘'] > 0).all(), "开盘价必须为正"

    # 检查高低关系
    assert (df['高'] >= df['低']).all(), "最高价必须≥最低价"
    assert (df['高'] >= df['收盘']).all(), "最高价必须≥收盘价"
    assert (df['低'] <= df['收盘']).all(), "最低价必须≤收盘价"

    # 检查成交量为正
    assert (df['成交量'] >= 0).all(), "成交量必须≥0"

    # 检查异常涨跌幅
    if '涨跌幅' in df.columns:
        assert (df['涨跌幅'].abs() <= 20).all(), "涨跌幅不应超过20%"

    return True
```

---

## 测试覆盖率改进建议

### 需要增加的测试场景

#### 1. strategy.py (当前64%，目标80%+)

**缺失测试**:
- 未测试的代码行: 65-66, 81-83, 86-105, 109-113 等

**需要增加的场景**:
- 极端市场情况（连续涨停/跌停）
- 成交量异常波动
- 价格缺口（跳空高开/低开）
- 策略参数边界值测试
- 多次买卖循环测试

**建议测试用例**:
```python
def test_volume_breakout_extreme_volatility():
    """测试极端波动情况"""
    # 创建连续涨停数据
    pass

def test_volume_breakout_gap_up():
    """测试跳空高开"""
    pass

def test_volume_breakout_multiple_trades():
    """测试多次交易循环"""
    pass
```

#### 2. backtest_engine.py (当前79%，目标85%+)

**未覆盖代码**: 主程序入口 (129-144行)

**建议**: 可忽略，或创建E2E测试

#### 3. data_manager.py (当前77%，目标85%+)

**未覆盖代码**: 命令行工具入口 (341-397行)

**建议**:
- 创建CLI测试
- 或标记为@pytest.mark.skip（如果不是核心功能）

---

## 总结

### Bug统计

| 编号 | 严重程度 | 状态 | 模块 | 影响 |
|------|----------|------|------|------|
| Bug #1 | HIGH | 未修复 | backtest_engine.py | 指标计算错误 |
| Bug #2 | MEDIUM | 待确认 | strategy.py | 测试假设可能错误 |

### 潜在问题统计

| 编号 | 严重程度 | 模块 | 类型 |
|------|----------|------|------|
| Issue #1 | HIGH | strategy.py | 前视偏差 |
| Issue #2 | MEDIUM | strategy.py | 交易成本 |
| Issue #3 | LOW | data_fetcher.py | 数据质量 |

### 优先级排序

1. 🔴 **立即修复**: Bug #1 (除零保护)
2. 🟡 **需要确认**: Bug #2 (移动止盈逻辑)
3. 🟡 **需要评估**: Issue #1 (前视偏差)
4. 🟢 **长期改进**: Issue #2 (交易成本)
5. 🟢 **长期改进**: Issue #3 (数据质量)

---

**报告生成时间**: 2026-02-16
**下次审查**: 修复Bug #1后
