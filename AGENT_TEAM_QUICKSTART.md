# Agent Team 快速开始指南

## 一句话总结

四个Agent各司其职，添加4个可配置参数到股票回测系统。

## 你是谁？选择你的角色

### 我是 Config-Manager (配置管理员)
**你的任务**: 设计和实现配置参数
**预计时间**: 2-3小时
**开始阅读**: `AGENT_TEAM_SPAWN_PROMPTS.md` → 团队1️⃣ 部分

**快速任务清单**:
- [ ] 修改 `strategy_config.json` (新增4个参数)
- [ ] 修改 `config.py` (新增30行代码)
- [ ] 修改 `app_with_cache.py` (新增40行API代码)
- [ ] 测试两个API端点
- [ ] 通知其他团队

**关键文件**:
```
D:\ai_work\stock_test\strategy_config.json
D:\ai_work\stock_test\config.py
D:\ai_work\stock_test\app_with_cache.py
```

**第一步**: 打开 `AGENT_TEAM_SPAWN_PROMPTS.md` 中的 **团队1️⃣** 部分

---

### 我是 Backtest-Engine-Dev (回测引擎开发者)
**你的任务**: 实现交易成本计算逻辑
**预计时间**: 3-4小时
**前置条件**: 等待 config-manager 完成
**开始阅读**: `AGENT_TEAM_SPAWN_PROMPTS.md` → 团队2️⃣ 部分

**快速任务清单**:
- [ ] 了解config-manager的参数设计
- [ ] 修改 `backtest_engine.py` 的 `__init__()` 方法
- [ ] 添加4个新方法
- [ ] 更新 `run_single_stock()` 方法
- [ ] 测试计算准确性
- [ ] 通知qa-tester

**关键文件**:
```
D:\ai_work\stock_test\backtest_engine.py
D:\ai_work\stock_test\strategy.py (仅查看)
```

**第一步**: 等待 config-manager 的通知，然后打开 `AGENT_TEAM_SPAWN_PROMPTS.md` 中的 **团队2️⃣** 部分

---

### 我是 Frontend-Developer (前端UI开发者)
**你的任务**: 创建参数配置界面
**预计时间**: 3-4小时
**前置条件**: 等待 config-manager 完成
**开始阅读**: `AGENT_TEAM_SPAWN_PROMPTS.md` → 团队3️⃣ 部分

**快速任务清单**:
- [ ] 了解config-manager的参数设计
- [ ] 修改 `templates/index_with_cache.html` (新增400行)
- [ ] 添加HTML表单元素
- [ ] 添加CSS样式
- [ ] 添加JavaScript交互逻辑
- [ ] 测试表单验证和API调用
- [ ] 通知qa-tester

**关键文件**:
```
D:\ai_work\stock_test\templates\index_with_cache.html
```

**第一步**: 等待 config-manager 的通知，然后打开 `AGENT_TEAM_SPAWN_PROMPTS.md` 中的 **团队3️⃣** 部分

---

### 我是 QA-Tester (测试验证员)
**你的任务**: 编写测试并验证所有功能
**预计时间**: 3-4小时
**前置条件**: 等待其他3个团队完成
**开始阅读**: `AGENT_TEAM_SPAWN_PROMPTS.md` → 团队4️⃣ 部分

**快速任务清单**:
- [ ] 创建 `tests/test_backtest_new_features.py` (300+行)
- [ ] 创建 `test_config_flow.py` (100+行)
- [ ] 运行单元测试
- [ ] 运行集成测试
- [ ] 手动测试所有功能
- [ ] 生成 `TEST_REPORT.md`
- [ ] 报告问题或确认完成

**关键文件**:
```
D:\ai_work\stock_test\tests\test_backtest_new_features.py (新建)
D:\ai_work\stock_test\test_config_flow.py (新建)
D:\ai_work\stock_test\TEST_REPORT.md (新建)
```

**第一步**: 等待其他3个团队的完成通知，然后打开 `AGENT_TEAM_SPAWN_PROMPTS.md` 中的 **团队4️⃣** 部分

---

## 总体流程图

```
开始项目
   │
   ├─ Config-Manager 启动
   │  └─ 完成后通知其他团队 ✓
   │
   ├─ Backtest-Engine-Dev 和 Frontend-Developer 并行
   │  ├─ 完成后通知 QA-Tester
   │  └─ 并行执行
   │
   └─ QA-Tester 启动
      └─ 验证所有功能
         ├─ 全部通过 → 项目完成!
         └─ 发现问题 → 反馈给相关团队 → 修改 → 重新测试
```

## 四个参数速查表

| 参数 | 英文名 | 默认值 | 范围 | 公式/说明 |
|------|--------|--------|------|-----------|
| 初始资金 | initial_capital | 100000 | 10k-10M | 用于计算持仓数量 |
| 交易占比 | position_ratio | 0.2 | 1%-99% | position_size = IC * PR / price |
| 手续费 | commission_rate | 0.001 | 0%-100% | cost = amount * rate |
| 滑点 | slippage | 0.0 | 0%-5% | buy*1.05, sell*0.95 |

## 关键公式速查

### 1. 持仓数量 (backtest-engine-dev)
```python
position_size = floor(initial_capital * position_ratio / current_price)
# 按手(100股)取整
```

### 2. 滑点应用 (backtest-engine-dev)
```python
买入价 = 原价 * (1 + slippage)
卖出价 = 原价 * (1 - slippage)
```

### 3. 手续费 (backtest-engine-dev)
```python
交易成本 = 交易金额 * commission_rate
```

## API端点速查

### 获取配置 (config-manager + frontend-developer)
```
GET /api/backtest/settings

返回:
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

### 更新配置 (config-manager + frontend-developer)
```
POST /api/backtest/settings

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

## 文件清单

### 修改的文件
```
□ strategy_config.json          (config-manager)
□ config.py                     (config-manager)
□ app_with_cache.py             (config-manager - API部分)
□ backtest_engine.py            (backtest-engine-dev)
□ templates/index_with_cache.html (frontend-developer)
```

### 新建的文件
```
□ tests/test_backtest_new_features.py (qa-tester)
□ test_config_flow.py                  (qa-tester)
□ TEST_REPORT.md                       (qa-tester)
```

## 项目目录结构

```
D:\ai_work\stock_test\
├── strategy_config.json              ← config-manager
├── config.py                         ← config-manager
├── app_with_cache.py                 ← config-manager (部分)
├── backtest_engine.py                ← backtest-engine-dev
├── strategy.py                       (不修改)
├── templates/
│   └── index_with_cache.html         ← frontend-developer
├── tests/
│   └── test_backtest_new_features.py ← qa-tester (新建)
├── test_config_flow.py               ← qa-tester (新建)
├── TEST_REPORT.md                    ← qa-tester (新建)
├── AGENT_TEAM_SPAWN_PROMPTS.md       (详细工作指令)
├── AGENT_TEAM_COORDINATION.md        (协调指南)
└── AGENT_TEAM_QUICKSTART.md          (本文件)
```

## 常见问题 (FAQ)

### Q: 我应该从哪里开始？
A: 根据你的角色打开对应的 Spawn Prompts 文档。config-manager 应该首先启动，其他人等待 config-manager 完成。

### Q: 如果我完成得早了怎么办？
A: 通知其他团队，这样他们可以更早开始工作。你也可以帮助其他团队或进行额外的测试。

### Q: 如果遇到问题了怎么办？
A:
1. 首先在 Spawn Prompts 文档中查找解答
2. 检查相关文件的注释和代码
3. 向相关团队发出通知，说明你的阻塞点
4. 在 `AGENT_TEAM_COORDINATION.md` 中查看问题上报流程

### Q: 参数应该存在哪里？
A:
- 定义: `config.py` (常量)
- 存储: `strategy_config.json` (JSON文件)
- 读取: `config_manager.py` (ConfigManager类)

### Q: 如何测试我的工作？
A: 查看对应 Spawn Prompts 中的"验收标准"部分，按照清单逐项检查。

### Q: 需要修改什么文件？
A: 查看 Spawn Prompts 中的"文件所有权"部分，只修改指定的文件。

## 验收标准快速检查

### Config-Manager 完成检查
- [ ] strategy_config.json 包含4个新参数
- [ ] config.py 新增常量和验证函数
- [ ] app_with_cache.py 新增2个API端点
- [ ] 测试API端点工作正常
- [ ] 通知其他团队

### Backtest-Engine-Dev 完成检查
- [ ] BacktestEngine 接受4个新参数
- [ ] 4个新方法已实现
- [ ] run_single_stock 应用新的计算
- [ ] 回测结果包含 backtest_settings
- [ ] 代码无语法错误
- [ ] 通知 QA-Tester

### Frontend-Developer 完成检查
- [ ] 配置面板HTML已添加
- [ ] CSS样式已应用
- [ ] JavaScript逻辑已实现
- [ ] 表单验证正确
- [ ] 参数集成到回测流程
- [ ] 页面无报错

### QA-Tester 完成检查
- [ ] 单元测试文件已创建
- [ ] 所有单元测试通过
- [ ] 集成测试文件已创建
- [ ] 所有集成测试通过
- [ ] 测试报告已生成
- [ ] 无已知BUG

## 重要提示

⚠️ **顺序很重要**:
- Config-Manager **必须**先完成
- Backtest-Engine-Dev 和 Frontend-Developer 可以**并行**
- QA-Tester **必须**等待其他3个完成

⚠️ **通讯很重要**:
- 完成工作后立即通知相关团队
- 遇到问题立即通知相关团队
- 定期更新进度

⚠️ **质量很重要**:
- 代码应该清晰、有注释
- 所有验收标准都应该满足
- 测试应该全面、可重复

## 快速联系

如果需要帮助或有问题：

1. 查看 `AGENT_TEAM_SPAWN_PROMPTS.md` 的详细说明
2. 查看 `AGENT_TEAM_COORDINATION.md` 的协调指南
3. 查看代码中的现有注释和文档
4. 向相关团队发出通知

## 开始工作

**现在就开始吧!**

→ 如果你是 **Config-Manager**: 打开 `AGENT_TEAM_SPAWN_PROMPTS.md` 中的 **团队1️⃣** 部分

→ 其他角色: 等待 config-manager 完成，然后打开对应的部分

---

**祝你工作顺利!** 🚀

