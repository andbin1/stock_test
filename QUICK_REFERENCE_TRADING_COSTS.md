# 交易成本计算 - 快速参考指南

## 公式速查

### 持仓数量
```
amount = 初始资金 × 交易占比 ÷ 买入价
position = floor(amount ÷ 100) × 100  # 按手取整
```
**例**: 10万 × 0.2 ÷ 10元 = 2000股

### 价格调整
```
买入价 = 原价 × (1 + 滑点)
卖出价 = 原价 × (1 - 滑点)
```
**例**: 10元，1%滑点 → 买10.1元，卖9.9元

### 手续费
```
成本 = 交易金额 × 手续费率
```
**例**: 10万 × 0.1% = 100元

### 收益率
```
利润 = 卖出额 - 买入额 - 手续费
收益率 = 利润 ÷ (买入额 + 手续费) × 100
```

---

## 参数对照表

| 参数 | 最小 | 默认 | 最大 | 单位 |
|------|------|------|------|------|
| initial_capital | 10k | 100k | 10M | 元 |
| position_ratio | 0.01 | 0.2 | 0.99 | % |
| commission_rate | 0 | 0.001 | 0.05 | % |
| slippage | 0 | 0.0 | 0.05 | % |

---

## 常见场景

### 场景1: 保守型交易（低成本）
```python
engine = BacktestEngine(
    initial_capital=100000,   # 10万
    position_ratio=0.1,       # 每笔10%
    commission_rate=0.0005,   # 0.05%
    slippage=0.0              # 无滑点
)
```

### 场景2: 标准型交易（中等成本）
```python
engine = BacktestEngine(
    initial_capital=100000,   # 10万
    position_ratio=0.2,       # 每笔20%
    commission_rate=0.001,    # 0.1%
    slippage=0.005            # 0.5%
)
```

### 场景3: 激进型交易（高成本）
```python
engine = BacktestEngine(
    initial_capital=100000,   # 10万
    position_ratio=0.3,       # 每笔30%
    commission_rate=0.002,    # 0.2%
    slippage=0.02             # 2%
)
```

### 场景4: 仅考虑手续费
```python
engine = BacktestEngine(
    commission_rate=0.001,    # 0.1%
    slippage=0.0              # 无滑点
)
```

### 场景5: 仅考虑滑点
```python
engine = BacktestEngine(
    commission_rate=0,        # 无手续费
    slippage=0.01             # 1%
)
```

---

## 使用方式

### 方式1: 默认参数
```python
engine = BacktestEngine()
# 使用所有默认值
```

### 方式2: 部分自定义
```python
engine = BacktestEngine(
    initial_capital=50000
    # 其他参数使用默认值
)
```

### 方式3: 完全自定义
```python
engine = BacktestEngine(
    initial_capital=100000,
    position_ratio=0.2,
    commission_rate=0.001,
    slippage=0.01
)
```

### 方式4: 从配置获取
```python
from config_manager import ConfigManager

config = ConfigManager()
settings = config.get_trading_settings()
engine = BacktestEngine(**settings)
```

---

## API 调用

### 获取当前配置
```bash
GET /api/backtest/settings
```

### 更新配置
```bash
POST /api/backtest/settings
{
    "initial_capital": 100000,
    "position_ratio": 0.2,
    "commission_rate": 0.001,
    "slippage": 0.01
}
```

### 执行回测（自动使用配置）
```bash
POST /api/backtest/cache
{
    "symbols": ["000001", "000002"],
    "strategy": "volume_breakout"
}
```

---

## 输出数据

### 每笔交易包含
```python
{
    '买入日期': '2025-01-01',
    '买入价': 10.1,              # 含滑点
    '卖出日期': '2025-01-05',
    '卖出价': 10.395,            # 含滑点
    '持仓数量': 1900,            # 按手取整
    '买入成本': 19.19,           # 手续费
    '卖出成本': 19.75,           # 手续费
    '收益率%': 2.71,             # 扣除成本后
    '状态': '平仓'
}
```

### 回测结果包含
```python
{
    'symbol': '000001',
    'trades': [...],             # 交易列表
    'total_return': 25.80,       # 总收益率
    'num_trades': 9,             # 交易数
    'win_rate': 77.8,            # 胜率
    'avg_return': 2.87,          # 平均收益
    'max_loss': -0.50,           # 最大亏损
    'profit_factor': 1.42,       # 盈亏比
    'backtest_settings': {...}   # 配置信息
}
```

---

## 示例计算

### 完整交易成本计算

**参数**:
- 初始资金: 100,000元
- 交易占比: 0.2 (20%)
- 手续费率: 0.1% (0.001)
- 滑点: 1% (0.01)

**交易**:
- 买入价: 10.0元
- 卖出价: 10.5元
- 持有天数: 5天

**计算过程**:

1. **应用滑点**
   - 买入价 = 10.0 × (1 + 0.01) = 10.1元
   - 卖出价 = 10.5 × (1 - 0.01) = 10.395元

2. **计算持仓**
   - amount = 100000 × 0.2 ÷ 10.1 = 1980.20股
   - position = floor(1980.20 ÷ 100) × 100 = 1900股

3. **计算金额**
   - 买入额 = 10.1 × 1900 = 19,190元
   - 卖出额 = 10.395 × 1900 = 19,750.5元

4. **计算手续费**
   - 买入费 = 19,190 × 0.001 = 19.19元
   - 卖出费 = 19,750.5 × 0.001 = 19.75元

5. **计算收益**
   - 利润 = 19,750.5 - 19,190 - 19.19 - 19.75 = 521.56元
   - 总成本 = 19,190 + 19.19 + 19.75 = 19,228.94元
   - 收益率 = 521.56 ÷ 19,228.94 × 100 = 2.71%

**结果**: 交易收益率 2.71%（扣除所有成本）

---

## 对标真实成本

### 中国A股典型成本

| 成本类型 | 费率 | 说明 |
|---------|------|------|
| 佣金 | 0.01%-0.03% | 券商收费 |
| 印花税 | 0.1% | 仅卖出 |
| 过户费 | 0.002% | 很少使用 |
| 滑点 | 0.5%-2% | 市场执行成本 |

**建议设置**:
```python
# 中等流动性股票
commission_rate = 0.002    # 0.2%(含佣金和印花税)
slippage = 0.01            # 1%

# 高流动性股票（大盘股）
commission_rate = 0.0012   # 0.12%
slippage = 0.005           # 0.5%

# 低流动性股票（小盘股）
commission_rate = 0.003    # 0.3%
slippage = 0.02            # 2%
```

---

## 常见问题

### Q: 为什么我的收益下降了这么多？
**A**: 这正常！滑点和手续费会显著影响收益。这正是模拟真实交易的原因。

### Q: 能否关闭成本计算？
**A**: 可以，设置 `commission_rate=0, slippage=0`

### Q: 我的参数设置合理吗？
**A**: 参考A股真实成本：
- 佣金: 0.01%-0.03%
- 印花税: 0.1% (仅卖出)
- 滑点: 0.5%-2% (取决于流动性)

### Q: 同一持仓的成本如何计算？
**A**: 按持仓时间计数，每次交易都独立计算成本

### Q: 持仓数量为什么会变少？
**A**: 滑点增加了买入成本，同样资金购买的股数会减少

---

## 命令行使用

### 获取配置状态
```bash
python config_manager.py status
```

### 修改参数
```bash
python config_manager.py set initial_capital 50000
python config_manager.py set commission_rate 0.002
python config_manager.py set slippage 0.01
```

### 保存预设
```bash
python config_manager.py save-preset 保守型
python config_manager.py save-preset 激进型
```

### 加载预设
```bash
python config_manager.py load-preset 保守型
```

---

## 文件位置

| 内容 | 位置 |
|------|------|
| 核心实现 | D:\ai_work\stock_test\backtest_engine.py |
| 配置管理 | D:\ai_work\stock_test\config_manager.py |
| API集成 | D:\ai_work\stock_test\app_with_cache.py |
| 单元测试 | D:\ai_work\stock_test\test_trading_cost_engine.py |
| 集成测试 | D:\ai_work\stock_test\test_integration_trading_costs.py |
| 技术文档 | D:\ai_work\stock_test\TRADING_COST_ENGINE_IMPLEMENTATION.md |

---

## 支持的策略

所有策略都自动支持成本计算：

- ✓ VolumeBreakoutStrategy（量能突破）
- ✓ SteadyTrendStrategy（稳健趋势）
- ✓ AggressiveMomentumStrategy（激进动量）
- ✓ BalancedMultiFactorStrategy（平衡多因子）
- ✓ DoubleMACrossStrategy（双均线）
- ✓ GridTradingStrategy（网格交易）
- ✓ TurtleTradingStrategy（海龟法则）

---

*快速参考指南*
*2026-02-24*
