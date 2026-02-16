# 使用指南

## 三种使用方式

### 方式1️⃣: 完整回测（推荐首先使用）

运行完整的沪深300和中证500回测：

```bash
python main.py
```

**特点**：
- 获取两个指数的全部成分股
- 进行完整回测
- 生成详细报告和图表
- 耗时：首次15-30分钟（取决于网络）

**输出**：
- `回测汇总对比.csv` - 两个指数对比
- `详细交易记录_*.csv` - 详细交易
- `回测摘要_*.png` - 图表
- `股票走势_*.png` - 样本走势

---

### 方式2️⃣: 快速测试（验证策略逻辑）

运行快速测试，验证5只著名股票的交易信号：

```bash
python quick_test.py
```

**特点**：
- 只测试5只样本股票
- 快速了解策略是否有效
- 耗时：2-3分钟
- 可以看到详细的交易过程

**适用场景**：
- 新改参数后想快速验证
- 想看策略的具体交易明细

**示例输出**：
```
📊 测试股票: 000001
   周期: 20200101 ~ 20250213
   参数: {...}

📈 交易信号:
     日期    收盘     MA5    MA30  Buy_Signal  Sell_Signal
2024-03-15  10.50   10.45   10.40       True       False
2024-03-18  10.55   10.52   10.42      False        True

💰 交易记录:
   买入日期  买入价  卖出日期  卖出价  持有天数  收益率%    状态
2024-03-15   10.50 2024-03-18  10.55      3      0.38%   平仓

✅ 统计:
   总交易数: 12
   总收益: 15.45%
   ...
```

---

### 方式3️⃣: 参数优化（找最优参数）

网格搜索找到最优的策略参数：

```bash
python param_optimizer.py
```

**特点**：
- 自动尝试多个参数组合
- 找出最优参数
- 耗时：30-60分钟（取决于参数数量）

**输出**：
- `参数优化结果.csv` - 所有参数组合的结果排名

**参数搜索范围**（可在代码中修改）：
```python
param_ranges = {
    "ma_period": [20, 30, 40],           # MA周期
    "volume_multiplier": [1.5, 2.0, 2.5],# 量能倍数
    "hold_days": [2, 3, 4],              # 持有天数
}
```

**示例输出**：
```
ma_period  volume_multiplier  hold_days  trades  total_return  avg_return  win_rate  profit_factor
    20            1.5           2        145       285.34%      1.97%       63.4%      1.92
    30            2.0           3        132       287.45%      2.18%       62.1%      1.85
    40            2.5           4        98        265.12%      2.71%       60.2%      1.78
```

---

## 调整策略参数

### 文件：`config.py`

```python
STRATEGY_PARAMS = {
    "ma_period": 30,          # 30日均线周期（改为20/40试试）
    "recent_days": 5,         # 量能检查周期（很少改动）
    "retest_period": 5,       # 回踩均线周期（很少改动）
    "hold_days": 3,           # 持有天数（改为2/5试试）
    "volume_multiplier": 2.0, # 量能放大倍数（改为1.5/2.5试试）
}
```

### 参数调整指南

**问题: 交易次数太少**
- 降低 `volume_multiplier`（从2.0降到1.5）
- 或降低 `ma_period`（从30降到20）

**问题: 胜率太低**
- 提高 `volume_multiplier`（从2.0升到2.5）
- 或延长 `hold_days`（从3天增加到4-5天）

**问题: 平均收益太小**
- 缩短 `hold_days`（从3天减少到2天）
- 或降低 `volume_multiplier`（要求放大条件宽松）

**问题: 回测不相信**
- 检查时间段 `START_DATE` 和 `END_DATE`
- 检查是否有足够的股票数据

---

## 修改后如何重新运行

1. 编辑 `config.py` 中的参数

2. 根据需求选择运行方式：

   ```bash
   # 快速验证新参数（推荐）
   python quick_test.py

   # 如果满意，再运行完整回测
   python main.py
   ```

3. 查看输出文件验证结果

---

## 文件说明

| 文件 | 说明 | 修改? |
|------|------|------|
| `main.py` | 主程序入口 | ❌ 不建议改 |
| `config.py` | 配置文件 | ✅ 需要改参数时修改 |
| `strategy.py` | 策略实现 | ⚠️ 高级用户才改 |
| `data_fetcher.py` | 数据获取 | ❌ 不建议改 |
| `backtest_engine.py` | 回测引擎 | ❌ 不建议改 |
| `visualizer.py` | 图表绘制 | ❌ 不建议改 |
| `quick_test.py` | 快速测试 | ✅ 可改测试股票 |
| `param_optimizer.py` | 参数优化 | ✅ 可改搜索范围 |

---

## 常见工作流

### 工作流1: 快速验证想法

```
1. 修改 config.py 参数
2. python quick_test.py       # 快速看效果
3. 满意后 python main.py      # 完整回测
4. 查看生成的CSV和图表
```

### 工作流2: 参数优化

```
1. 修改 param_optimizer.py 的搜索范围
2. python param_optimizer.py   # 运行30-60分钟
3. 查看 参数优化结果.csv
4. 将最优参数复制到 config.py
5. python main.py             # 最终验证
```

### 工作流3: 对比不同策略

```
1. 保存当前最优参数
2. 修改参数试新想法
3. python quick_test.py
4. 记录几个关键指标
5. 恢复参数，与之前对比
```

---

## 性能优化建议

### 降低回测时间

在 `config.py` 中：
```python
MAX_STOCKS = 50  # 改为50而不是全部（约300+只）
```

### 快速开发

```bash
# 方式1: 快速测试 -> 满意后完整回测
python quick_test.py

# 方式2: 在param_optimizer.py中缩小搜索范围
param_ranges = {
    "ma_period": [25, 30, 35],        # 改为只3个值
    "volume_multiplier": [1.8, 2.0],  # 改为只2个值
}
```

---

## 常见错误

### 错误1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'akshare'
```

**解决**：
```bash
pip install -r requirements.txt
```

### 错误2: 数据获取失败

```
获取成分股失败: ...
```

**原因**：网络问题或akshare服务不稳定

**解决**：
- 检查网络连接
- 过几分钟重试
- 如果持续失败，可能是akshare的API变化了

### 错误3: 内存不足

```
MemoryError
```

**解决**：
- 在 `config.py` 中减少 `MAX_STOCKS`
- 缩短 `START_DATE` 到 `END_DATE` 的时间范围

---

## 数据来源

所有数据通过开源库 `akshare` 获取：
- 指数成分股信息：tencent/sina
- 历史行情数据：东方财富/新浪财经

无需付费，无需API密钥。

---

## 获取帮助

需要更多帮助？

1. 查看代码中的注释
2. 查看 `README.md` 的概念解释
3. 检查输出的CSV文件理解数据含义
4. 修改代码中的 `print()` 语句进行调试

---

**版本**: 1.0
**最后更新**: 2025-02-13
