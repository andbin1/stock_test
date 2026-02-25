# 回测引擎I/O规范与执行规则

## 概述

本文档详细定义了回测引擎的输入输出规范、交易执行假设、以及各种边界条件的处理方式。确保回测结果的可重复性和可信度。

---

## 第1部分：输入数据规范

### 1.1 K线数据格式

#### 1.1.1 数据结构

```python
# 输入格式：Pandas DataFrame
# 行数：至少50条交易日记录
# 列数：7列（见下表）

import pandas as pd

kline_data = pd.DataFrame({
    '日期': pd.date_range('2024-01-01', periods=100, freq='D'),
    '开盘': [10.00, 10.05, ...],
    '高': [10.10, 10.15, ...],
    '低': [9.95, 10.00, ...],
    '收盘': [10.05, 10.10, ...],
    '成交量': [1000000, 1100000, ...],
    '成交额': [10050000, 11105000, ...],
})
```

#### 1.1.2 数据列详细要求

| 列名 | 类型 | 范围 | 说明 |
|------|------|------|------|
| 日期 | datetime64 | - | 交易日期，必须升序 |
| 开盘 | float64 | > 0 | 开盘价格，元 |
| 高 | float64 | ≥ max(O,H,L,C) | 最高价格，元 |
| 低 | float64 | ≤ min(O,H,L,C) | 最低价格，元 |
| 收盘 | float64 | > 0 | 收盘价格，元 |
| 成交量 | int64 | ≥ 0 | 成交量，股数 |
| 成交额 | float64 | ≥ 0 | 成交额，元 |

#### 1.1.3 数据有效性检查

```python
def validate_kline_data(df: pd.DataFrame) -> bool:
    """验证K线数据的有效性"""

    # 检查1：必需列
    required = ['日期', '开盘', '高', '低', '收盘', '成交量', '成交额']
    if not all(col in df.columns for col in required):
        raise ValueError(f"缺少必需列，需要: {required}")

    # 检查2：行数
    if len(df) < 50:
        raise ValueError(f"数据不足，需要至少50行，实际{len(df)}行")

    # 检查3：数据类型
    assert pd.api.types.is_datetime64_any_dtype(df['日期'])
    assert pd.api.types.is_numeric_dtype(df['开盘'])

    # 检查4：OHLC逻辑一致性
    assert (df['高'] >= df['开盘']).all(), "高 < 开盘"
    assert (df['高'] >= df['收盘']).all(), "高 < 收盘"
    assert (df['高'] >= df['低']).all(), "高 < 低"
    assert (df['低'] <= df['开盘']).all(), "低 > 开盘"
    assert (df['低'] <= df['收盘']).all(), "低 > 收盘"

    # 检查5：价格非负
    assert (df['开盘'] > 0).all(), "开盘价 ≤ 0"
    assert (df['收盘'] > 0).all(), "收盘价 ≤ 0"
    assert (df['成交量'] >= 0).all(), "成交量 < 0"
    assert (df['成交额'] >= 0).all(), "成交额 < 0"

    # 检查6：日期递增
    assert df['日期'].is_monotonic_increasing, "日期未递增"

    # 检查7：没有重复日期
    assert not df['日期'].duplicated().any(), "存在重复日期"

    return True
```

### 1.2 策略参数规范

#### 1.2.1 参数配置结构

```python
# 所有策略都使用统一的参数字典格式
strategy_params = {
    # 通用参数
    'name': '策略名称',
    'version': '1.0',

    # 具体参数（根据策略而定）
    'ma_period': 30,
    'volume_multiplier': 2.0,
    # ...
}
```

#### 1.2.2 参数验证

```python
def validate_strategy_params(params: dict, strategy_type: str) -> bool:
    """验证策略参数的有效性"""

    # 检查必需参数
    required_params = {
        'volume_breakout': ['ma_period', 'hold_days', 'volume_multiplier'],
        'steady_trend': ['ma_short', 'ma_long', 'stop_loss', 'take_profit'],
        'aggressive_momentum': ['rsi_period', 'rsi_threshold', 'max_hold_days'],
        'balanced_multi_factor': ['boll_period', 'rsi_period', 'min_factor_score'],
    }

    required = required_params.get(strategy_type, [])
    if not all(param in params for param in required):
        raise ValueError(f"缺少必需参数: {required}")

    # 检查参数范围
    assert params['ma_period'] > 0, "ma_period 必须 > 0"
    assert 0 < params['volume_multiplier'] < 10, "volume_multiplier 范围: (0, 10)"

    return True
```

### 1.3 初始化参数

```python
# 回测初始化参数
backtest_config = {
    'initial_capital': 100000,      # 初始资金，元
    'commission_rate': 0.00025,     # 手续费万2.5
    'stamp_tax': 0.001,             # 印花税千1
    'slippage': 0.001,              # 滑点0.1%
    'trading_fee_min': 5.0,         # 最低手续费5元
    'start_date': '2024-01-01',     # 回测开始日期
    'end_date': '2024-12-31',       # 回测结束日期
}
```

---

## 第2部分：输出结果规范

### 2.1 单只股票结果

#### 2.1.1 结果结构

```python
single_stock_result = {
    'symbol': '000001',             # 股票代码
    'name': '平安银行',             # 股票名称
    'period': '2024-01-01~2024-12-31',

    # 交易列表
    'trades': [
        {
            '买入日期': pd.Timestamp('2024-01-10'),
            '买入价': 10.00,
            '买入金额': 1000.00,

            '卖出日期': pd.Timestamp('2024-01-15'),
            '卖出价': 11.00,
            '卖出金额': 1100.00,

            '持有天数': 5,

            '毛收益': 100.00,        # 元
            '毛收益率%': 10.00,

            '交易成本': 13.20,       # 元
            '交易成本率%': 1.32,

            '净收益': 86.80,         # 元
            '净收益率%': 8.68,

            '状态': '平仓',          # 平仓/未平仓/止损/止盈/死叉等
        },
        # ... 更多交易
    ],

    # 统计指标
    'statistics': {
        'num_trades': 12,
        'winning_trades': 8,
        'losing_trades': 4,
        'win_rate': 66.67,           # %
        'loss_rate': 33.33,          # %

        'total_gross_profit': 850.00,    # 元
        'total_gross_loss': -450.00,     # 元
        'total_net_profit': 400.00,      # 元

        'avg_trade_profit': 33.33,       # 元
        'avg_winning_trade': 106.25,     # 元
        'avg_losing_trade': -112.50,     # 元

        'total_return': 0.40,            # 40%（相对初始资金）
        'avg_return_per_trade': 3.33,    # %
        'max_single_return': 12.5,       # %
        'min_single_return': -8.2,       # %

        'profit_factor': 1.89,           # 盈亏比
        'max_drawdown': -0.12,           # -12%
    }
}
```

#### 2.1.2 关键字段说明

```python
# 收益率的层级关系
毛收益率 = (卖出价 - 买入价) / 买入价

交易成本率 = 交易成本 / 买入金额

净收益率 = 毛收益率 - 交易成本率
         = (卖出价 - 买入价 - 交易成本) / 买入价

# 示例
买入价 = 10元，卖出价 = 11元，100股
买入金额 = 1000元

毛收益 = 100元
毛收益率 = 10%

交易成本 = 13.2元
交易成本率 = 1.32%

净收益 = 86.8元
净收益率 = 8.68%

验证：8.68% = 10% - 1.32% ✓
```

### 2.2 多只股票聚合结果

#### 2.2.1 聚合结构

```python
portfolio_result = {
    'summary': {
        'total_stocks': 20,              # 参与回测的股票数
        'stocks_with_trades': 18,        # 有交易的股票数
        'period': '2024-01-01~2024-12-31',
        'initial_capital': 100000,
        'final_capital': 124500,
    },

    'aggregated_trades': {
        'total_trades': 256,
        'total_winning_trades': 152,
        'total_losing_trades': 104,
        'win_rate': 59.38,               # %

        'total_gross_profit': 8500.00,
        'total_gross_loss': -3200.00,
        'total_trading_cost': 1300.00,
        'total_net_profit': 4000.00,     # 元
    },

    'risk_metrics': {
        # 收益指标
        'total_return': 0.04,            # 4%
        'annual_return': 0.04,           # 年化4%（1年）
        'avg_return_per_trade': 1.56,    # %

        # 风险指标
        'max_drawdown': -0.15,           # -15%
        'annual_volatility': 0.18,       # 18%

        # 风险调整收益
        'sharpe_ratio': 0.95,
        'calmar_ratio': 0.27,
        'sortino_ratio': 1.2,
        'profit_factor': 2.05,

        # 单笔交易
        'avg_winning_trade': 5.59,       # %
        'avg_losing_trade': -3.08,       # %
        'max_single_return': 25.3,       # %
        'min_single_return': -12.5,      # %
    },

    'stock_details': [
        {
            'symbol': '000001',
            'num_trades': 12,
            'total_return': 0.08,
            # ... 个股详情
        },
        # ... 更多股票
    ]
}
```

#### 2.2.2 聚合方法

```python
def aggregate_results(all_stock_results: dict) -> dict:
    """聚合所有股票的回测结果"""

    # 收集所有交易
    all_trades = []
    for symbol, result in all_stock_results.items():
        all_trades.extend(result['trades'])

    # 计算聚合指标
    total_trades = len(all_trades)
    returns = [t['净收益率%'] / 100 for t in all_trades]

    # 胜率
    wins = sum(1 for t in all_trades if t['净收益率%'] > 0)
    win_rate = wins / total_trades * 100

    # 盈亏比
    profits = [t['净收益'] for t in all_trades if t['净收益'] > 0]
    losses = [abs(t['净收益']) for t in all_trades if t['净收益'] < 0]
    profit_factor = sum(profits) / sum(losses) if losses else float('inf')

    # 最大回撤
    cumulative = np.cumprod([1 + r for r in returns])
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'max_drawdown': max_dd,
        # ... 其他指标
    }
```

---

## 第3部分：交易执行规则

### 3.1 信号触发条件

#### 3.1.1 买入信号执行

```
时刻 T：收到买入信号
价格采用：T日收盘价
执行价 = 收盘价 + 滑点
       = 收盘价 × (1 + 0.1%)

手续费 = max(执行价 × 100股 × 0.025%, 5元)

成交后状态：持仓建立
```

#### 3.1.2 卖出信号执行

```
时刻 T：收到卖出信号
价格采用：T日收盘价
执行价 = 收盘价 - 滑点
       = 收盘价 × (1 - 0.1%)

成本明细：
  手续费 = max(执行价 × 100股 × 0.025%, 5元)
  印花税 = 执行价 × 100股 × 0.1%
  滑点   = 执行价 × 100股 × 0.1%

成交后状态：头寸平仓
```

### 3.2 成交量限制

#### 3.2.1 市场冲击限制

```python
# 假设不应在单日内成交超过该日成交量的5%
max_tradeable_volume = day_volume * 0.05

# 如果回测中某个信号会导致总成交量 > 5%
if total_volume > max_tradeable_volume:
    # 方案1：拒绝该交易
    skip_trade()

    # 方案2：延迟到下一个交易日
    delay_trade(days=1)
```

### 3.3 A股交割规则 (T+1)

#### 3.3.1 交割周期

```
买入日期 T：
  - T日：买入确认
  - T+1日：资金冻结，不能交易该股
  - T+2日：可以卖出

卖出日期 T：
  - T日：卖出确认
  - T+1日：资金到账，可用于其他交易
```

#### 3.3.2 实现规则

```python
def can_trade(symbol, current_date, last_trade_date):
    """检查是否可以交易该股票"""

    if last_trade_date is None:
        return True  # 没有交易历史，可以交易

    days_elapsed = (current_date - last_trade_date).days

    if days_elapsed >= 1:
        return True  # 满足T+1规则
    else:
        return False  # 违反T+1规则，不能交易
```

### 3.4 信号冲突处理

#### 3.4.1 同日买卖冲突

```
如果在同一交易日同时收到买入和卖出信号：
  优先级1：先执行已持仓的卖出信号
  优先级2：然后执行新的买入信号

原理：控制风险，先平仓后建仓
```

#### 3.4.2 多信号冲突

```
如果有多个不同类型的卖出信号（止损、止盈、死叉）：
  优先级1：止损（保护本金）
  优先级2：止盈（锁定收益）
  优先级3：技术信号（趋势反转）
```

### 3.5 持仓管理

#### 3.5.1 单位头寸

```
最小交易单位：100股（A股规则）

建议最少交易金额：4,000元
  - 低于此金额会触发5元最低手续费
  - 成本占比会升高到0.25%以上

最大持仓时间：由策略参数控制
  - 如果超过最大天数仍未卖出
  - 强制以市价卖出
```

#### 3.5.2 资金分配

```
初始资金：100,000元

策略1执行：购买000001，投入10,000元
可用资金：90,000元

策略2执行：购买000002，投入8,000元
可用资金：82,000元

注意：当前系统假设每只股票为独立回测
实际应该考虑总体头寸限制
```

---

## 第4部分：边界条件处理

### 4.1 数据不足

#### 4.1.1 回测启动期

```
回测开始前需要足够的历史数据用于指标计算：
  - MA30需要30个交易日
  - RSI需要14个交易日
  - MACD需要26个交易日

建议：回测开始日期前至少准备50个交易日数据
```

#### 4.1.2 股票数据不足处理

```python
def is_sufficient_data(df):
    """检查数据是否足够"""

    # 检查行数
    if len(df) < 50:
        return False

    # 检查最近交易日
    latest_date = df['日期'].max()
    days_stale = (today - latest_date).days
    if days_stale > 5:  # 超过5个交易日未更新
        return False

    return True
```

### 4.2 极端行情处理

#### 4.2.1 涨跌停限制

```
A股涨跌停规则：
  - 新股（上市首日）：无涨跌停限制
  - 普通股（上市第2+天）：±10%涨跌停
  - 科创板/北交所：±20%涨跌停

识别涨跌停：
  涨幅 = (收盘价 - 前一日收盘价) / 前一日收盘价

  如果 |涨幅| > 9.8%：认为该日涨跌停

处理方式：
  涨停日：无法卖出
  跌停日：无法买入

  在下一个非限制板的交易日执行交易
```

```python
def is_limit_up(df, idx):
    """检查是否涨停"""
    if idx == 0:
        return False
    change = (df['收盘'].iloc[idx] - df['收盘'].iloc[idx-1]) / df['收盘'].iloc[idx-1]
    return change > 0.098

def is_limit_down(df, idx):
    """检查是否跌停"""
    if idx == 0:
        return False
    change = (df['收盘'].iloc[idx] - df['收盘'].iloc[idx-1]) / df['收盘'].iloc[idx-1]
    return change < -0.098
```

#### 4.2.2 零成交量处理

```
零成交量天（停牌、暂停交易）：
  成交量 = 0

处理方式：
  - 不执行该天的交易
  - 持有的头寸暂停管理
  - 等待恢复交易
```

```python
def has_volume(df, idx):
    """检查是否有成交量"""
    return df['成交量'].iloc[idx] > 0
```

### 4.3 特殊情况处理

#### 4.3.1 除权除息

```
A股会进行定期除权除息：
  - 分红：每100股分多少元
  - 配股：每100股配多少股
  - 送股：每100股送多少股

影响：会导致价格和成交量的不连续

处理方式：
  - 使用复权K线（前复权或后复权）
  - 对历史价格进行复权调整

当前系统假设：输入的数据已经过前复权处理
```

#### 4.3.2 停牌重组

```
如果股票在回测期内停牌重组：
  状态：无法交易

处理方式：
  - 已持仓的头寸冻结
  - 新的交易信号被忽略
  - 复牌后恢复正常
```

### 4.4 资金管理

#### 4.4.1 资金不足

```
如果可用资金不足以执行某个买入信号：
  方案1：跳过该交易（推荐）
  方案2：等比例减少持仓数量

当前系统使用方案1
```

#### 4.4.2 融资融券

```
当前系统暂不支持：
  - 融资买入（借钱买股票）
  - 融券卖空（借股票卖空）

仅支持做多策略
```

---

## 第5部分：错误处理与日志

### 5.1 异常类型

```python
class BacktestException(Exception):
    """回测异常基类"""
    pass

class DataValidationError(BacktestException):
    """数据验证失败"""
    pass

class ParameterError(BacktestException):
    """参数配置错误"""
    pass

class ExecutionError(BacktestException):
    """交易执行异常"""
    pass
```

### 5.2 日志记录

```python
def log_trade(trade_info):
    """记录交易日志"""
    logger.info(f"""
    新交易:
    股票: {trade_info['symbol']}
    买入: {trade_info['buy_date']} @ {trade_info['buy_price']:.2f}
    卖出: {trade_info['sell_date']} @ {trade_info['sell_price']:.2f}
    收益: {trade_info['return']:.2f}%
    """)

def log_warning(message):
    """记录警告"""
    logger.warning(f"回测警告: {message}")
```

---

## 第6部分：性能考虑

### 6.1 时间复杂度

```
单只股票回测：O(n)
  其中 n = 交易日数

m只股票回测：O(m × n)

指标计算：O(n)
  - MA: 滑动窗口，O(n)
  - RSI: 迭代计算，O(n)
  - MACD: EMA，O(n)

总体复杂度：O(m × n × k)
  其中 k = 指标数量
```

### 6.2 优化建议

```
1. 指标缓存：预计算不变的指标
2. 批量处理：使用向量化操作而非循环
3. 并行计算：多个股票可以并行处理
4. 增量更新：只计算新增数据的指标
```

---

## 第7部分：验证与回溯测试

### 7.1 回测验证清单

```
[ ] 数据完整性检查
    [ ] 无缺失日期
    [ ] 无重复数据
    [ ] OHLC逻辑一致

[ ] 参数有效性检查
    [ ] 所有参数在有效范围内
    [ ] 无相互冲突的参数

[ ] 交易执行检查
    [ ] 所有买卖价格合理
    [ ] 成本计算准确
    [ ] 收益率计算正确

[ ] 结果合理性检查
    [ ] 收益率在合理范围
    [ ] 胜率在0-100%
    [ ] 最大回撤为负
    [ ] 交易数量合理
```

### 7.2 对标基准

```
对比标准：
  1. 沪深300指数 - 参照大盘表现
  2. 中证500指数 - 参照中小盘表现
  3. 创业板指数 - 参照成长股表现
  4. 无风险利率 - 参照保底收益

检查项：
  [ ] 年化收益 > 无风险利率
  [ ] 夏普比率 > 0.5
  [ ] 最大回撤 < 30%
  [ ] 胜率 > 45%
```

---

## 附录：典型错误与解决

### 问题A：回测结果过于完美（收益>50%）
**可能原因**：
1. 数据前向偏差（使用了未来数据）
2. 过度拟合（参数针对历史数据优化）
3. 成本计算不准确

**解决方案**：
1. 检查信号是否仅使用历史数据
2. 做样本外测试
3. 使用真实成本模型

### 问题B：回测与实盘差异大（>20%）
**可能原因**：
1. 滑点假设不符
2. 成交量限制未考虑
3. 涨跌停限制未处理

**解决方案**：
1. 调整滑点参数
2. 添加成交量检查
3. 添加涨跌停处理

### 问题C：交易数量异常（太少或太多）
**可能原因**：
1. 信号条件过于严格/松散
2. 指标计算有问题

**解决方案**：
1. 检查参数配置
2. 验证指标计算结果
3. 调整信号触发条件

---

## 结论

遵循本规范可以确保：
1. **数据质量**: 输入数据有效且完整
2. **执行准确**: 交易按规则准确执行
3. **结果可信**: 回测结果与真实交易接近
4. **可重复性**: 相同输入产生相同输出

建议在每次回测前都进行完整的验证，特别是对于新策略或新数据源。

