# Agent Team 四人协作项目

**项目启动**: 2026-02-24
**项目路径**: `D:\ai_work\stock_test`
**项目状态**: 🔵 准备中

## 项目目标

在股票回测系统中添加4项可配置参数：
1. ✓ 初始金额 (initial_capital)
2. ✓ 交易占比 (position_ratio)
3. ✓ 手续费 (commission_rate)
4. ✓ 滑点 (slippage)

使用户能在Web界面配置这些参数，并让回测引擎精确计算其影响。

---

## 📚 文档导航

### 🚀 快速开始
- **[AGENT_TEAM_QUICKSTART.md](AGENT_TEAM_QUICKSTART.md)** - 5分钟快速入门
  - 选择你的角色
  - 查看快速任务清单
  - 了解关键公式

### 📋 详细工作指南
- **[AGENT_TEAM_SPAWN_PROMPTS.md](AGENT_TEAM_SPAWN_PROMPTS.md)** - 详细的工作指令
  - 团队1️⃣ 配置管理员 - 360行详细指南
  - 团队2️⃣ 回测引擎开发者 - 380行详细指南
  - 团队3️⃣ 前端UI开发者 - 420行详细指南
  - 团队4️⃣ 测试验证员 - 340行详细指南

### 🎯 协调和管理
- **[AGENT_TEAM_COORDINATION.md](AGENT_TEAM_COORDINATION.md)** - 协调指南
  - 项目架构
  - 执行阶段
  - 团队沟通协议
  - 风险和缓解
  - 文件所有权

### 📊 任务追踪
- **[AGENT_TEAM_TASK_TRACKER.md](AGENT_TEAM_TASK_TRACKER.md)** - 任务管理
  - 4个主任务和子任务
  - 时间线
  - 进度指标
  - 每日更新模板

---

## 👥 四人团队角色

### 1️⃣ 配置管理员 (config-manager)
**职责**: 设计和实现配置参数系统
**文件**: strategy_config.json, config.py, app_with_cache.py
**预计时间**: 2-3小时
**优先级**: ⭐⭐⭐ 最高 (其他团队都依赖)

**快速任务**:
1. 修改 strategy_config.json (新增4个参数)
2. 修改 config.py (新增常量和验证函数)
3. 修改 app_with_cache.py (新增2个API端点)
4. 测试并通知其他团队

[→ 查看详细工作指南](AGENT_TEAM_SPAWN_PROMPTS.md#团队1️⃣-配置管理员-config-manager)

---

### 2️⃣ 回测引擎开发者 (backtest-engine-dev)
**职责**: 实现交易成本和滑点计算
**文件**: backtest_engine.py
**预计时间**: 3-4小时
**优先级**: ⭐⭐⭐ 最高
**前置条件**: ⚠️ 等待 config-manager 完成

**快速任务**:
1. 更新 BacktestEngine 类接受新参数
2. 实现4个新方法 (position_size, slippage, cost等)
3. 更新 run_single_stock() 应用新计算
4. 测试并通知 qa-tester

[→ 查看详细工作指南](AGENT_TEAM_SPAWN_PROMPTS.md#团队2️⃣-回测引擎开发者-backtest-engine-dev)

---

### 3️⃣ 前端UI开发者 (frontend-developer)
**职责**: 创建参数配置界面
**文件**: templates/index_with_cache.html
**预计时间**: 3-4小时
**优先级**: ⭐⭐⭐ 最高
**前置条件**: ⚠️ 等待 config-manager 完成

**快速任务**:
1. 添加配置面板HTML (初始资金、占比、手续费、滑点)
2. 添加CSS样式
3. 实现JavaScript交互逻辑 (加载、保存、验证)
4. 集成到回测流程，测试并通知 qa-tester

[→ 查看详细工作指南](AGENT_TEAM_SPAWN_PROMPTS.md#团队3️⃣-前端ui开发者-frontend-developer)

---

### 4️⃣ 测试验证员 (qa-tester)
**职责**: 编写测试并验证所有功能
**文件**: tests/test_backtest_new_features.py, test_config_flow.py
**预计时间**: 3-4小时
**优先级**: ⭐⭐⭐ 最高
**前置条件**: ⚠️ 等待其他3个团队完成

**快速任务**:
1. 创建单元测试 (参数验证、计算函数、极端情况)
2. 创建集成测试 (API、端到端流程)
3. 运行所有测试并记录结果
4. 生成测试报告，报告任何问题

[→ 查看详细工作指南](AGENT_TEAM_SPAWN_PROMPTS.md#团队4️⃣-测试验证员-qa-tester)

---

## 🔄 执行流程

### 阶段1: 配置设计 (Day 1) ← 现在在这里
```
config-manager 启动
    ↓ (2-3小时)
config-manager 完成并通知其他团队
```

**关键里程碑**:
- ✓ strategy_config.json 有效
- ✓ config.py 新增常量和验证
- ✓ API端点已实现并可用

---

### 阶段2: 并行实现 (Day 2-3)
```
config-manager 完成后
    ├─ backtest-engine-dev 启动 → 实现成本计算
    └─ frontend-developer 启动 → 实现配置界面

两个团队并行工作，各3-4小时
```

**关键里程碑**:
- ✓ 两个团队各完成代码实现
- ✓ 两个团队完成基本测试
- ✓ 两个团队通知 qa-tester

---

### 阶段3: 集成测试 (Day 4)
```
两个团队完成后
    ↓
qa-tester 启动
    ├─ 运行单元测试
    ├─ 运行集成测试
    └─ 手动测试所有功能

3-4小时完成测试
```

**关键里程碑**:
- ✓ 所有测试通过
- ✓ 功能验证无误
- ✓ 生成测试报告

---

### 阶段4: 反馈修改 (Day 5)
```
qa-tester 发现问题
    ├─ 报告给相关团队
    ↓
相关团队修复
    ↓
qa-tester 重新测试
    ↓
所有问题解决 → 项目完成!
```

**关键里程碑**:
- ✓ 所有问题已解决
- ✓ 最终验证通过
- ✓ 代码提交

---

## 📊 关键公式速查

### 1. 持仓数量计算
```
position_size = floor(initial_capital * position_ratio / current_price)
按手(100股)取整
```

### 2. 滑点应用
```
买入价 = 原价 × (1 + slippage)
卖出价 = 原价 × (1 - slippage)
```

### 3. 手续费计算
```
交易成本 = 交易金额 × commission_rate
应用到买卖两次
```

### 4. 参数范围
```
initial_capital:    10,000 ~ 10,000,000 (元)
position_ratio:     1% ~ 99%
commission_rate:    0% ~ 100% (但通常 < 5%)
slippage:           0% ~ 5%
```

---

## 🔗 API接口速查

### GET /api/backtest/settings
获取当前配置
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

### POST /api/backtest/settings
更新配置
```json
请求:
{
    "initial_capital": 100000,
    "position_ratio": 0.2,
    "commission_rate": 0.001,
    "slippage": 0.0
}

返回:
{
    "success": true,
    "message": "配置已更新",
    "settings": { ... }
}
```

---

## 📁 文件所有权矩阵

| 文件 | 所有者 | 修改量 | 操作 |
|------|--------|--------|------|
| strategy_config.json | config-manager | 新增部分 | 修改 |
| config.py | config-manager | +30行 | 修改 |
| backtest_engine.py | backtest-engine-dev | +150行 | 修改 |
| templates/index_with_cache.html | frontend-developer | +400行 | 修改 |
| app_with_cache.py | config-manager | +40行 | 修改 (仅API) |
| tests/test_backtest_new_features.py | qa-tester | 新建 | 创建 |
| test_config_flow.py | qa-tester | 新建 | 创建 |
| TEST_REPORT.md | qa-tester | 新建 | 创建 |

**所有权规则**:
- 只有所有者可以修改文件
- 修改前通知其他使用者
- 完成后立即提交
- 发现冲突立即通知

---

## ✅ 验收标准清单

项目完成必须满足以下所有标准：

### 功能性
- ✓ 所有4个参数可在Web界面配置
- ✓ 参数正确传递到回测引擎
- ✓ 回测结果正确反映参数影响
- ✓ 不同配置产生不同结果 (可验证)
- ✓ 参数持久化 (保存后可读取)

### 可靠性
- ✓ 无代码语法错误
- ✓ 所有参数验证规则有效
- ✓ API返回正确格式
- ✓ 极端情况处理正确 (无崩溃)
- ✓ 计算精确度 > 99.9%

### 测试覆盖
- ✓ 单元测试 > 80%覆盖率
- ✓ 集成测试通过 100%
- ✓ 手动测试清单完成
- ✓ 性能测试无问题
- ✓ 无已知BUG

### 代码质量
- ✓ 代码有清晰注释
- ✓ 遵循项目编码规范
- ✓ 变量命名清晰
- ✓ 函数职责单一
- ✓ 没有重复代码

### 文档完整
- ✓ 参数文档清晰
- ✓ API文档完整
- ✓ 公式文档准确
- ✓ 测试报告完成
- ✓ 代码注释充分

---

## 🚨 常见问题 (FAQ)

### Q: 我应该从哪里开始？
**A**:
1. 找到你的角色 (上面的5个人之一)
2. 打开对应的 Spawn Prompts 文档
3. 按照详细指南逐步执行

### Q: 我完成得快怎么办？
**A**:
1. 检查验收标准是否全部满足
2. 通知其他团队可以开始
3. 帮助被阻塞的团队
4. 进行额外的测试或优化

### Q: 遇到问题怎么办？
**A**:
1. 查看 SPAWN_PROMPTS 中的详细说明
2. 查看代码中的注释
3. 向相关团队发出通知
4. 查看 COORDINATION 指南中的问题上报流程

### Q: 需要多长时间？
**A**: 总共4-5个工作日
- Day 1: config-manager (2-3小时)
- Day 2-3: backtest-engine-dev + frontend-developer (6-8小时)
- Day 4: qa-tester (3-4小时)
- Day 5: 反馈修改 (1-2小时)

### Q: 如果代码冲突怎么办？
**A**: 不应该发生，因为每个团队的文件所有权很清晰。如果发生：
1. 立即通知相关团队
2. 协商解决方案
3. 重新提交代码

---

## 📞 沟通指南

### 完成某项工作时
```
标题: ✓ [任务名称] 完成

内容:
- 任务编号: #[n]
- 完成时间: [时间]
- 输出物: [文件/代码]
- 下一步: [谁应该继续]
- 问题: [是否有问题]
```

### 遇到问题时
```
标题: ⚠️ [严重度] [问题描述]

内容:
- 问题所在: [文件/代码]
- 影响范围: [哪些工作受影响]
- 需要帮助: [具体需要什么]
- 时间紧急: [低/中/高]
```

---

## 🎯 最后的话

### 为什么这个项目重要

这4个参数是回测系统最关键的成本因素。实现好这些功能，能确保：
- 用户得到可信的回测结果
- 系统具有完整的配置灵活性
- 为未来的功能奠定基础

### 成功的关键

1. **清晰沟通** - 及时通知进度
2. **相互理解** - 理解他人的约束
3. **质量第一** - 宁慢勿乱
4. **记录完善** - 便于日后维护
5. **主动协作** - 帮助被阻塞的团队

### 预期成果

项目完成后：
- ✓ 系统拥有完整的参数配置能力
- ✓ 所有功能经过充分测试
- ✓ 代码质量高、文档完整
- ✓ 团队成员有良好的协作体验
- ✓ 为后续开发打下坚实基础

---

## 📖 推荐阅读顺序

1. **首先**: 本文件 (README) - 5分钟了解全局
2. **其次**: QUICKSTART.md - 10分钟找到你的角色
3. **然后**: 对应的 SPAWN_PROMPTS 部分 - 30分钟精读
4. **参考**: COORDINATION.md - 了解整体架构
5. **跟踪**: TASK_TRACKER.md - 记录进度

---

## 🔗 快速链接

| 文档 | 用途 | 阅读时间 |
|------|------|---------|
| AGENT_TEAM_README.md | 项目概览 (本文件) | 15分钟 |
| AGENT_TEAM_QUICKSTART.md | 快速开始 | 10分钟 |
| AGENT_TEAM_SPAWN_PROMPTS.md | 详细工作指南 | 60分钟 |
| AGENT_TEAM_COORDINATION.md | 协调指南 | 30分钟 |
| AGENT_TEAM_TASK_TRACKER.md | 任务追踪 | 20分钟 |

---

## 📅 重要日期

| 日期 | 事件 | 状态 |
|------|------|------|
| 2026-02-24 | 项目启动 | ✓ |
| 2026-02-24 | config-manager 启动 | - |
| 2026-02-25 | backtest-engine-dev 和 frontend-developer 启动 | - |
| 2026-02-27 | qa-tester 启动 | - |
| 2026-02-28 | 项目完成预期 | - |

---

## 🏁 项目完成标志

当以下所有条件都满足时，项目完成：

```
✓ Config-Manager 完成 + 通知其他团队
✓ Backtest-Engine-Dev 完成 + 通知 QA-Tester
✓ Frontend-Developer 完成 + 通知 QA-Tester
✓ QA-Tester 完成 + 所有测试通过
✓ 所有问题已解决
✓ 代码已提交
✓ 文档已更新
✓ 团队满意度 > 90%
```

---

**项目路径**: `D:\ai_work\stock_test`
**项目启动**: 2026-02-24
**最后更新**: 2026-02-24

**祝项目顺利!** 🚀

