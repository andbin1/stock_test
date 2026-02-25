# 交易成本计算引擎实现文档

## 概述

本文档详细说明了回测引擎中交易成本计算模块的实现。该模块支持以下功能：

1. 初始资金管理
2. 单笔交易占比控制
3. 手续费计算
4. 滑点处理
5. 完整的交易成本应用流程

---

## 核心参数

### 参数结构

```python
{
    'initial_capital': 100000,      # 初始资金（元）
    'position_ratio': 0.2,          # 单笔交易占比（0-1）
    'commission_rate': 0.001,       # 手续费率（0-1）
    'slippage': 0.0                 # 滑点（0-1）
}
```

### 参数范围

| 参数 | 最小值 | 默认值 | 最大值 | 说明 |
|------|--------|--------|--------|------|
| initial_capital | 10,000元 | 100,000元 | 10,000,000元 | 回测起始资金 |
| position_ratio | 0.01 | 0.2 | 0.99 | 每笔交易占总资金比例 |
| commission_rate | 0 | 0.001 | 0.05 | 手续费率（万分比）|
| slippage | 0 | 0.0 | 0.05 | 滑点率（百分比）|

---

## BacktestEngine 类

### 初始化方法

```python
def __init__(self, initial_capital: float = None, position_ratio: float = None,
             commission_rate: float = None, slippage: float = None):
```

**功能**：初始化回测引擎，设置交易参数

**参数说明**：
- 所有参数可选，未提供时使用 `config.py` 中的默认值
- 自动生成 `backtest_settings` 字典，用于结果返回

**示例**：
```python
engine = BacktestEngine(
    initial_capital=100000,
    position_ratio=0.2,
    commission_rate=0.001,
    slippage=0.01
)
```

---

## 核心方法

### 1. calculate_position_size(price: float) -> int

**目标**：根据当前股票价格计算持仓数量

**公式**：
```
amount = initial_capital × position_ratio ÷ price
position_size = floor(amount ÷ 100) × 100
```

**说明**：
- 结果按手(100股)取整
- 确保每笔交易都是100股的整数倍（A股交易规则）

**示例**：
```python
engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)
# 股价10元时：100000 × 0.2 ÷ 10 = 2000股
position = engine.calculate_position_size(10)  # 返回 2000
```

---

### 2. apply_slippage_to_price(price: float, is_buy: bool) -> float

**目标**：应用滑点到交易价格

**公式**：
- 买入：`price_with_slip = price × (1 + slippage)`
- 卖出：`price_with_slip = price × (1 - slippage)`

**说明**：
- 滑点模拟市场执行成本
- 买入增加成本，卖出降低收益
- 反映真实交易的不完美执行

**示例**：
```python
engine = BacktestEngine(slippage=0.01)  # 1%滑点
buy_price = engine.apply_slippage_to_price(10.0, is_buy=True)   # 10.1
sell_price = engine.apply_slippage_to_price(10.0, is_buy=False) # 9.9
```

---

### 3. calculate_trade_cost(amount: float) -> float

**目标**：计算单次交易的手续费

**公式**：
```
cost = amount × commission_rate
```

**说明**：
- 买入和卖出各计算一次手续费
- 基于实际交易金额计算
- 采用百分比模式

**示例**：
```python
engine = BacktestEngine(commission_rate=0.001)  # 0.1%
# 交易金额100000元时
cost = engine.calculate_trade_cost(100000)  # 返回 100.0
```

---

### 4. apply_trading_costs(trade: dict) -> dict

**目标**：对单笔交易应用完整的成本计算流程

**输入**：原始交易记录（来自策略的 get_trades()）
```python
{
    '买入日期': '2025-01-01',
    '买入价': 10.0,
    '卖出日期': '2025-01-05',
    '卖出价': 10.5,
    '持有天数': 4,
    '收益率%': 5.0,
    '状态': '平仓'
}
```

**处理流程**：

1. **应用滑点**
   ```
   买入价_含滑点 = apply_slippage_to_price(买入价, is_buy=True)
   卖出价_含滑点 = apply_slippage_to_price(卖出价, is_buy=False)
   ```

2. **计算持仓数量**
   ```
   持仓数量 = calculate_position_size(买入价_含滑点)
   ```

3. **计算交易金额**
   ```
   买入金额 = 买入价_含滑点 × 持仓数量
   卖出金额 = 卖出价_含滑点 × 持仓数量
   ```

4. **计算手续费**
   ```
   买入手续费 = calculate_trade_cost(买入金额)
   卖出手续费 = calculate_trade_cost(卖出金额)
   ```

5. **重新计算收益率**
   ```
   总成本 = 买入金额 + 买入手续费 + 卖出手续费
   利润 = 卖出金额 - 买入金额 - 买入手续费 - 卖出手续费
   收益率% = (利润 ÷ 总成本) × 100
   ```

**输出**：更新后的交易记录
```python
{
    '买入日期': '2025-01-01',
    '买入价': 10.1,              # 已应用滑点
    '卖出日期': '2025-01-05',
    '卖出价': 10.395,            # 已应用滑点
    '持有天数': 4,
    '持仓数量': 1900,            # 新增：计算的持仓数量
    '买入成本': 19.19,           # 新增：买入手续费
    '卖出成本': 19.75,           # 新增：卖出手续费
    '收益率%': 2.71,             # 重新计算：扣除所有成本
    '状态': '平仓'
}
```

---

### 5. run_single_stock(symbol: str, df: pd.DataFrame, strategy: Any) -> dict

**目标**：对单只股票运行回测，自动应用成本计算

**关键改进**：

1. 获取策略交易信号：`trades = strategy.get_trades(df)`

2. **应用成本计算到每笔交易**：
   ```python
   trades_with_costs = [self.apply_trading_costs(trade) for trade in trades]
   ```

3. 计算回测统计指标
   - 总收益率
   - 平均收益率
   - 胜率
   - 盈亏比
   - 最大单笔亏损

4. **返回结果包含**：
   ```python
   {
       'symbol': symbol,
       'trades': trades_with_costs,           # 含成本信息
       'total_return': total_return,
       'num_trades': num_trades,
       'win_rate': win_rate,
       'avg_return': avg_return,
       'max_loss': max_loss,
       'profit_factor': profit_factor,
       'backtest_settings': backtest_settings # 新增：配置信息
   }
   ```

---

## 集成点

### API 端点

#### GET /api/backtest/settings
获取当前回测配置

**响应**：
```json
{
    "success": true,
    "settings": {
        "initial_capital": 100000,
        "position_ratio": 0.2,
        "commission_rate": 0.001,
        "slippage": 0.0
    }
}
```

#### POST /api/backtest/settings
更新回测配置

**请求**：
```json
{
    "initial_capital": 100000,
    "position_ratio": 0.2,
    "commission_rate": 0.001,
    "slippage": 0.01
}
```

#### POST /api/backtest/cache
执行回测（自动使用当前设置）

**关键代码**：
```python
# 获取交易设置
trading_settings = config_manager.get_trading_settings()

# 创建引擎（自动应用设置）
engine = BacktestEngine(
    initial_capital=trading_settings['initial_capital'],
    position_ratio=trading_settings['position_ratio'],
    commission_rate=trading_settings['commission_rate'],
    slippage=trading_settings['slippage']
)

# 执行回测
results = engine.run_multiple_stocks(all_data, strategy)
```

---

## 使用示例

### 示例1：基础使用

```python
from backtest_engine import BacktestEngine
from strategy import VolumeBreakoutStrategy
from config import STRATEGY_PARAMS

# 初始化引擎
engine = BacktestEngine(
    initial_capital=100000,
    position_ratio=0.2,
    commission_rate=0.001,
    slippage=0.01
)

# 执行回测
strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
result = engine.run_single_stock("000001", df, strategy)

# 查看结果
print(f"交易数: {result['num_trades']}")
print(f"总收益: {result['total_return']:.2f}%")
print(f"平均收益: {result['avg_return']:.2f}%")

# 查看单笔交易详情
for trade in result['trades']:
    print(f"买入: {trade['买入价']:.2f} 卖出: {trade['卖出价']:.2f} 数量: {trade['持仓数量']}")
```

### 示例2：多策略对比

```python
# 配置A：保守型（低成本）
engine_conservative = BacktestEngine(
    initial_capital=100000,
    position_ratio=0.1,
    commission_rate=0.0005,
    slippage=0.0
)

# 配置B：激进型（高成本）
engine_aggressive = BacktestEngine(
    initial_capital=100000,
    position_ratio=0.3,
    commission_rate=0.002,
    slippage=0.02
)

# 对比结果
results_a = engine_conservative.run_single_stock(symbol, df, strategy)
results_b = engine_aggressive.run_single_stock(symbol, df, strategy)

print(f"保守型收益: {results_a['total_return']:.2f}%")
print(f"激进型收益: {results_b['total_return']:.2f}%")
```

---

## 验证与测试

### 运行测试

```bash
cd D:\ai_work\stock_test
python test_trading_cost_engine.py
```

### 测试覆盖

- ✓ 持仓数量计算（按手取整）
- ✓ 滑点应用（买卖方向）
- ✓ 手续费计算（基于金额）
- ✓ 完整成本流程（集成测试）
- ✓ 回测设置集成（参数传递）

---

## 关键公式速查

| 操作 | 公式 | 说明 |
|------|------|------|
| 持仓数量 | floor(IC × PR ÷ P ÷ 100) × 100 | 按手(100股)取整 |
| 买入价 | P × (1 + S) | S为滑点率 |
| 卖出价 | P × (1 - S) | S为滑点率 |
| 买入手续费 | BP × PS × CR | BP=买入价,PS=持仓数,CR=手续费率 |
| 卖出手续费 | SP × PS × CR | SP=卖出价 |
| 收益率 | (SP×PS - BP×PS - 手续费) ÷ (BP×PS + 手续费) × 100 | 扣除所有成本 |

其中：
- IC = 初始资金 (Initial Capital)
- PR = 交易占比 (Position Ratio)
- P = 股票价格
- S = 滑点 (Slippage)
- CR = 手续费率 (Commission Rate)

---

## 常见问题

### Q1: 为什么使用滑点后持仓数量会变少？

**A**: 这是正确的。滑点增加了买入成本，同样的资金能购买的股数会减少。

```
例：初始资金10万，交易占比0.2，原价10元
- 不含滑点：100000 × 0.2 ÷ 10 = 2000股
- 含1%滑点：100000 × 0.2 ÷ 10.1 ≈ 1980股（按手取整为1900股）
```

### Q2: 收益率为什么下降了？

**A**: 因为我们现在计算了真实的交易成本。原始策略中的收益率只是价格变化，未扣除手续费和滑点。

### Q3: 如何只测试滑点影响？

**A**: 设置 `commission_rate=0`, `slippage=0.01`

### Q4: 如何只测试手续费影响？

**A**: 设置 `commission_rate=0.001`, `slippage=0`

---

## 后续任务

本模块完成后，接下来的任务由其他团队成员负责：

1. **QA测试员** (`qa-tester`)：
   - 验证成本计算的准确性
   - 测试边界情况
   - 性能基准测试

2. **前端开发者** (`frontend-dev`)：
   - 在Web界面显示成本明细
   - 实现参数实时调整
   - 可视化成本影响分析

3. **集成测试** (`integration-tester`)：
   - 端到端流程验证
   - 与现有系统集成测试

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `backtest_engine.py` | 核心实现（已更新） |
| `app_with_cache.py` | API集成（已更新） |
| `config.py` | 参数定义（无需修改） |
| `config_manager.py` | 参数管理（无需修改） |
| `test_trading_cost_engine.py` | 单元测试（新增） |

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-02-24 | 初始实现，包含4个核心方法 |

---

## 开发者联系

如有任何问题，请联系：
- **回测引擎开发者** (backtest-engine-dev)
- **配置管理员** (config-admin)

---

*最后更新: 2026-02-24*
