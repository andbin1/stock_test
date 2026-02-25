# Agent Team: Backtest Methodology Overhaul

## Goal
修复回测方法论的致命缺陷，实现专业级的成本计算、风险指标和真实收益评估。

## Team Composition

### 1. quant-trader (量化交易员) - Opus
- **角色**: 交易算法设计师，定义回测框架的数学模型
- **关键职责**:
  - 设计完整的成本模型和真实收益计算
  - 定义风险指标（MaxDD、Sharpe、Calmar等）
  - 审查所有交易逻辑的真实性
  - 输出详细的算法设计文档

### 2. backend-engineer (软件工程师) - Sonnet
- **角色**: 代码实现和重构专家
- **关键职责**:
  - 根据算法设计实现BacktestEngine
  - 实现新增的风险指标计算模块
  - 确保代码质量和可维护性
  - 集成现有系统，保持向后兼容

### 3. qa-engineer (测试工程师) - Sonnet
- **角色**: 回测准确性和质量保证
- **关键职责**:
  - 设计针对性的测试用例
  - 验证风险指标计算的正确性
  - 对比优化前后的结果
  - 确保回测结果可信度

## File Ownership

### quant-trader 拥有
- `backtest_spec.md` (新增，算法设计文档)
- `backtest_metrics_design.md` (新增，指标设计)

### backend-engineer 拥有
- `backtest_engine_v2.py` (重构版本)
- `risk_metrics.py` (新增，风险指标计算)
- `trading_cost_v2.py` (新增，完整成本模型)

### qa-engineer 拥有
- `tests/test_backtest_v2.py` (新增，测试套件)
- `tests/test_risk_metrics.py` (新增)

### 其他文件（不修改）
- `backtest_engine.py` (保留，作为参考)
- `trading_cost.py` (保留)
- `strategy.py` (保留)

## Task Breakdown

### quant-trader 任务

**Task 1**: 设计完整的成本模型（Deliverable: backtest_spec.md第1章）
- 分离买入成本和卖出成本
- 考虑最低手续费、成交额阈值
- 定义成本百分比计算方法
- 给出具体的数值示例

**Task 2**: 定义核心风险指标（Deliverable: backtest_metrics_design.md）
- 最大回撤 (Max Drawdown)
- 年化收益率 (Annualized Return)
- 年化波动率 (Annualized Volatility)
- 夏普比率 (Sharpe Ratio)
- 卡玛比率 (Calmar Ratio)
- 索提诺比率 (Sortino Ratio)
- 盈亏比 (Profit Factor)
- 胜率 (Win Rate)
- 单笔最大亏损 (Max Loss)
- 每个指标的计算公式、数据依赖、边界条件

**Task 3**: 审查策略信号逻辑（Deliverable: strategy_review.md）
- 识别VolumeBreakoutStrategy的问题
- 识别SteadyTrendStrategy的问题
- 给出修复建议
- 指出哪些问题会导致虚假信号

**Task 4**: 定义回测引擎输入输出规范（Deliverable: backtest_spec.md第2章）
- 输入: DataFrame格式、必需字段
- 输出: 回测结果数据结构
- 交易执行假设（价格、滑点、限价等）
- 处理特殊情况（停牌、涨跌停、除权）

### backend-engineer 任务

**Task 5**: 实现风险指标计算模块（Deliverable: risk_metrics.py）
- 实现Task 2中定义的所有指标
- 使用numpy/pandas高效计算
- 添加详细的注释和错误处理
- 输出：完整的模块代码

**Task 6**: 实现完整成本模型（Deliverable: trading_cost_v2.py）
- 基于Task 1的设计实现
- 处理最低手续费、四舍五入等细节
- 提供向量化计算接口
- 单位转换（亿元、万元、百分比）

**Task 7**: 重构BacktestEngine（Deliverable: backtest_engine_v2.py）
- 集成新的成本计算模块
- 集成新的风险指标模块
- 修复单股回测和批量回测逻辑
- 返回完整的性能指标
- 保持API兼容性（或清晰地标注破坏性改动）

**Task 8**: 代码审查和优化（消息给qa-engineer）
- 确保性能（大批量回测）
- 数值稳定性
- 边界条件处理

### qa-engineer 任务

**Task 9**: 设计测试用例（Deliverable: test_plan.md）
- 基于Task 2的指标定义设计单元测试
- 设计边界情况测试（空数据、单笔交易等）
- 设计集成测试
- 对比测试（旧vs新引擎）

**Task 10**: 实现测试套件（Deliverable: tests/test_*.py）
- 实现Task 9中设计的所有测试
- 覆盖所有新增功能
- 确保测试通过率100%

**Task 11**: 验证和回归测试（Deliverable: test_results.md）
- 运行完整的测试套件
- 对比优化前后的结果
- 给出质量保证报告
- 如发现不一致，反馈给quant-trader

**Task 12**: 集成验证（消息给backend-engineer）
- 验证新引擎与现有系统的兼容性
- 性能基准测试
- 提出优化建议

## Communication Protocol

### 交流节点

1. **quant-trader → backend-engineer**（Task 1-3完成后）
   - 分享 `backtest_spec.md` 和 `backtest_metrics_design.md`
   - 明确新算法的具体实现细节

2. **backend-engineer → qa-engineer**（Task 5-7完成后）
   - 分享新的API接口定义
   - 分享关键实现细节

3. **qa-engineer → quant-trader**（如发现问题）
   - 如测试结果与预期不符，提出疑问
   - 例："风险指标XXX的计算结果与预期差50%，是否算法理解有误？"

4. **backend-engineer → qa-engineer**（Task 8完成后）
   - 明确性能指标和约束条件
   - 分享关键的边界条件处理

### 信息示例

**qa-engineer 反馈给 quant-trader**:
```
发现问题：最大回撤计算
- 现象：测试用例的MaxDD为15%，但预期是12%
- 代码：在cumsum基础上，用running_max计算
- 问题：是否应该考虑未平仓头寸的未实现浮动亏损？
```

**backend-engineer 询问 quant-trader**:
```
实现疑问：成本计算
- config中的COMMISSION_RATE=0.00025（万2.5）
- 是否每笔交易都要检查最低手续费5元？
- 如何处理小额交易（买入5元*100股=500元）的情况？
```

## Coordination Settings

- **Delegate Mode**: 否（lead会参与部分验证）
- **Plan Approval**: 否（流程相对清晰）
- **Async**: 可以（Task无强依赖关系，quant可与backend并行）

## Definition of Done

✅ 完成条件：

1. **quant-trader**:
   - [ ] backtest_spec.md 完成（包含完整的成本和指标定义）
   - [ ] strategy_review.md 完成（指出问题和修复方案）
   - [ ] 通过qa-engineer的验证反馈

2. **backend-engineer**:
   - [ ] 三个新文件实现完成（risk_metrics.py / trading_cost_v2.py / backtest_engine_v2.py）
   - [ ] 所有代码通过qa-engineer的测试
   - [ ] 代码质量指标达标

3. **qa-engineer**:
   - [ ] 所有测试通过（100% pass rate）
   - [ ] test_results.md 完成
   - [ ] 确认新引擎与现有系统兼容

## Success Criteria

- ✅ 回测成本计算**逐笔精确**（不再固定0.1%）
- ✅ 风险指标**完整且可信**（MaxDD、Sharpe、Sortino等）
- ✅ 测试覆盖率 ≥ 85%
- ✅ 对比旧引擎，新引擎数据差异可解释
- ✅ 代码可直接用于生产环境
