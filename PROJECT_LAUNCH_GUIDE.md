# Agent Team 项目启动指南

**启动日期**: 2026-02-24
**项目代码**: STOCK-BACKTEST-V3
**项目类型**: 功能开发 + 集成测试
**团队规模**: 4个 Agent (串行+并行)
**预计周期**: 4-5个工作日

---

## 📢 项目启动信息

### 项目使命
在股票回测系统中集成4项重要的交易参数配置功能，使系统能够真实模拟实际交易成本。

### 核心需求
```
需求1: 初始金额配置 (initial_capital)
  ├─ 用于计算每笔交易的持仓数量
  ├─ 范围: 10k ~ 10M 元
  └─ 默认: 100k 元

需求2: 交易占比配置 (position_ratio)
  ├─ 每笔交易占初始资金的比例
  ├─ 范围: 1% ~ 99%
  └─ 默认: 20% (1/5)

需求3: 手续费配置 (commission_rate)
  ├─ 交易成本计算因子
  ├─ 范围: 0% ~ 100%
  └─ 默认: 0.1% (万1)

需求4: 滑点配置 (slippage)
  ├─ 模拟市场冲击成本
  ├─ 范围: 0% ~ 5%
  └─ 默认: 0%
```

### 交付成果
```
✓ 修改5个现有文件 (~650行新代码)
✓ 新建3个测试文件 (~750行测试代码)
✓ 编写4份详细工作指南 (~1500行文档)
✓ 创建1份任务追踪表
✓ 所有功能经过测试验证
```

---

## 🎯 项目目标

### 功能目标 (MUST HAVE)
- [ ] 所有4个参数可在Web界面配置
- [ ] 参数可正确保存和读取
- [ ] 参数正确传递到回测引擎
- [ ] 回测结果反映参数的真实影响

### 质量目标 (SHOULD HAVE)
- [ ] 测试覆盖率 > 80%
- [ ] 计算精确度 > 99.9%
- [ ] 代码无语法错误
- [ ] 文档完整清晰

### 时间目标
- [ ] Day 1: 配置系统完成
- [ ] Day 3: 回测引擎和前端完成
- [ ] Day 4: 测试验证完成
- [ ] Day 5: 问题修复完成

---

## 👥 团队组成和角色

### 团队成员1: 配置管理员
**名字**: config-manager
**职责**: 参数定义、API设计、配置管理
**工作时间**: 2-3小时 (最高优先级)
**关键输出**: 参数定义清晰、API可用

### 团队成员2: 回测引擎开发者
**名字**: backtest-engine-dev
**职责**: 成本计算、交易精确执行
**工作时间**: 3-4小时 (中等优先级，依赖team1)
**关键输出**: 计算准确、逻辑清晰

### 团队成员3: 前端UI开发者
**名字**: frontend-developer
**职责**: 用户界面、参数输入、交互设计
**工作时间**: 3-4小时 (中等优先级，依赖team1)
**关键输出**: 界面美观、交互流畅

### 团队成员4: 测试验证员
**名字**: qa-tester
**职责**: 测试设计、功能验证、质量保证
**工作时间**: 3-4小时 (中等优先级，依赖team2/3)
**关键输出**: 测试全面、问题清晰

---

## 📋 工作流程 (4个阶段)

### 🟢 阶段1: 配置设计 (Day 1 上午)

**Leader**: config-manager
**Duration**: 2-3小时

#### 关键任务
1. 修改 `strategy_config.json` 添加4个参数
2. 在 `config.py` 新增常量定义（30行）
3. 编写参数验证函数
4. 在 `app_with_cache.py` 添加2个API端点（40行）

#### 成功指标
- ✓ JSON 有效，无语法错误
- ✓ API 端点可正常调用
- ✓ 参数验证规则完整
- ✓ 完成后通知其他团队

**→ 详细指南: [AGENT_TEAM_SPAWN_PROMPTS.md 团队1部分](AGENT_TEAM_SPAWN_PROMPTS.md#团队1️⃣-配置管理员-config-manager)**

---

### 🟡 阶段2: 并行实现 (Day 2-3)

**Leaders**: backtest-engine-dev + frontend-developer
**Duration**: 6-8小时 (并行执行)

#### 2A: 回测引擎更新
**负责人**: backtest-engine-dev

**任务**:
1. 更新 `BacktestEngine` 类的 `__init__()` 方法
2. 实现4个新方法:
   - `calculate_position_size()` - 计算持仓数量
   - `apply_slippage_to_price()` - 应用滑点
   - `calculate_trade_cost()` - 计算手续费
3. 更新 `run_single_stock()` 应用新计算
4. 确保结果包含 `backtest_settings` 信息

**成功指标**:
- ✓ 持仓数量计算正确
- ✓ 滑点应用逻辑正确
- ✓ 手续费计算准确
- ✓ 单/多股票回测正常

**→ 详细指南: [AGENT_TEAM_SPAWN_PROMPTS.md 团队2部分](AGENT_TEAM_SPAWN_PROMPTS.md#团队2️⃣-回测引擎开发者-backtest-engine-dev)**

#### 2B: 前端UI实现
**负责人**: frontend-developer

**任务**:
1. 在 `templates/index_with_cache.html` 添加配置面板
2. 添加4个参数输入元素（初始资金、占比、手续费、滑点）
3. 实现参数预览和计算
4. 添加JavaScript交互逻辑（加载、保存、验证）
5. 集成到回测提交流程

**成功指标**:
- ✓ UI界面美观可用
- ✓ 表单验证规则正确
- ✓ 参数预览计算准确
- ✓ 保存/加载功能正常
- ✓ 无JavaScript错误

**→ 详细指南: [AGENT_TEAM_SPAWN_PROMPTS.md 团队3部分](AGENT_TEAM_SPAWN_PROMPTS.md#团队3️⃣-前端ui开发者-frontend-developer)**

---

### 🔵 阶段3: 集成测试 (Day 4)

**Leader**: qa-tester
**Duration**: 3-4小时

#### 关键任务
1. 创建单元测试文件 `tests/test_backtest_new_features.py` (300+行)
2. 创建集成测试文件 `test_config_flow.py` (100+行)
3. 运行所有测试并记录结果
4. 执行手动功能测试
5. 生成测试报告 `TEST_REPORT.md`

#### 成功指标
- ✓ 单元测试覆盖 > 80%
- ✓ 所有测试通过 100%
- ✓ 无已知BUG
- ✓ 计算精确度验证 > 99.9%
- ✓ 文档完整

**→ 详细指南: [AGENT_TEAM_SPAWN_PROMPTS.md 团队4部分](AGENT_TEAM_SPAWN_PROMPTS.md#团队4️⃣-测试验证员-qa-tester)**

---

### 🟣 阶段4: 反馈修改 (Day 5)

**All Teams**
**Duration**: 1-2小时

#### 流程
```
QA-Tester 发现问题
    ↓ (报告清单)
相关团队修复
    ↓ (提交代码)
QA-Tester 重新验证
    ↓
问题全部解决 → 项目完成!
```

#### 成功指标
- ✓ 所有阻塞问题已解决
- ✓ 最终验证通过
- ✓ 代码提交完成

---

## 📚 文档体系

本项目提供了完整的文档支持：

| 文档 | 用途 | 内容 | 阅读时间 |
|------|------|------|---------|
| **AGENT_TEAM_README.md** | 项目总览 | 4页，项目概述和快速参考 | 15分钟 |
| **AGENT_TEAM_QUICKSTART.md** | 快速入门 | 3页，5分钟上手指南 | 10分钟 |
| **AGENT_TEAM_SPAWN_PROMPTS.md** | 工作指南 | 12页，4个团队的详细任务说明 | 60分钟 |
| **AGENT_TEAM_COORDINATION.md** | 协调指南 | 8页，项目管理和沟通协议 | 30分钟 |
| **AGENT_TEAM_TASK_TRACKER.md** | 任务追踪 | 6页，任务列表和进度跟踪 | 20分钟 |
| **PROJECT_LAUNCH_GUIDE.md** | 启动指南 | 本文件，项目概要和启动清单 | 15分钟 |

### 推荐阅读路径
```
1. 你是谁? → QUICKSTART.md 选择角色 (5分钟)
2. 做什么? → 对应部分的 SPAWN_PROMPTS.md (20分钟)
3. 全面了解 → AGENT_TEAM_README.md (15分钟)
4. 需要帮助? → AGENT_TEAM_COORDINATION.md (30分钟)
```

---

## 🚀 快速启动

### 第一步: 验证环境
```bash
cd "D:\ai_work\stock_test"

# 检查项目结构
ls strategy_config.json config.py app_with_cache.py backtest_engine.py
ls templates/index_with_cache.html

# 验证Python环境
python --version  # 应该 >= 3.7
```

### 第二步: 阅读文档
```
首先阅读: AGENT_TEAM_README.md (15分钟)
然后阅读: AGENT_TEAM_QUICKSTART.md (10分钟)
```

### 第三步: 分配角色
```
根据 QUICKSTART.md 的角色选择：
- 我是配置管理员? → 打开 SPAWN_PROMPTS.md 团队1部分
- 我是引擎开发者? → 等待team1完成，然后打开 团队2部分
- 我是前端开发者? → 等待team1完成，然后打开 团队3部分
- 我是测试员?     → 等待team2/3完成，然后打开 团队4部分
```

### 第四步: 按照指南工作
```
打开对应的 SPAWN_PROMPTS.md 部分，按照详细指南逐步执行
```

### 第五步: 跟踪进度
```
更新 AGENT_TEAM_TASK_TRACKER.md 中的进度信息
每日汇报完成情况
```

---

## 📊 关键度量

### 代码变更
```
修改现有文件:   5个
新增代码行:    650行
新增文件:      3个
新增测试代码:   750行
新增文档:      1500行
总计:          2900行+
```

### 时间预算
```
配置管理:       2-3小时  (config-manager)
引擎开发:       3-4小时  (backtest-engine-dev)
前端开发:       3-4小时  (frontend-developer)
测试验证:       3-4小时  (qa-tester)
反馈修改:       1-2小时  (all teams)
总计:          12-18小时 (4-5个工作日)
```

### 质量指标
```
测试覆盖率:     > 80%
计算精确度:     > 99.9%
代码文档率:     > 90%
BUG缺陷率:      0个关键BUG
团队满意度:     > 90%
```

---

## ✅ 启动前检查清单

### 环保准备
- [ ] Python 3.7+ 已安装
- [ ] Flask 已安装
- [ ] Pytest 已安装 (用于测试)
- [ ] 项目目录有写入权限

### 文档准备
- [ ] 所有指南文档已创建
- [ ] 所有团队成员已分配
- [ ] 联系方式已确认

### 流程准备
- [ ] 团队角色已明确
- [ ] 工作流程已理解
- [ ] 沟通协议已确认
- [ ] 时间安排已确定

### 代码准备
- [ ] 现有代码可正常运行
- [ ] 没有未提交的修改
- [ ] 备份已完成 (可选)

### 其他准备
- [ ] 是否需要支持 (已标记)
- [ ] 是否需要培训 (已标记)
- [ ] 是否有风险 (已评估)

---

## 🎓 团队前置要求

### 配置管理员 (config-manager)
**需要掌握**:
- Python 配置管理模式
- JSON 文件格式
- Flask REST API 设计
- 参数验证逻辑

**推荐阅读**:
- config.py 现有代码 (10分钟)
- strategy_config.json 结构 (5分钟)
- app_with_cache.py 中的现有API (15分钟)

### 回测引擎开发者 (backtest-engine-dev)
**需要掌握**:
- Python 面向对象编程
- Pandas 数据处理
- 金融交易计算
- 单元测试

**推荐阅读**:
- backtest_engine.py 现有代码 (20分钟)
- strategy.py 中的交易逻辑 (15分钟)
- 关键公式部分 (10分钟)

### 前端UI开发者 (frontend-developer)
**需要掌握**:
- HTML/CSS/JavaScript
- DOM 操作和事件处理
- AJAX API 调用
- 表单验证

**推荐阅读**:
- index_with_cache.html 现有代码 (20分钟)
- 现有表单实现 (15分钟)
- JavaScript 交互逻辑 (15分钟)

### 测试验证员 (qa-tester)
**需要掌握**:
- Pytest 框架
- 单元测试编写
- 集成测试设计
- 测试报告编写

**推荐阅读**:
- 现有测试文件 (如有) (15分钟)
- Pytest 基础 (20分钟)
- 测试覆盖率计算 (10分钟)

---

## 🔗 关键资源链接

### 内部文档
- 📄 [AGENT_TEAM_README.md](AGENT_TEAM_README.md) - 项目总览
- 📄 [AGENT_TEAM_QUICKSTART.md](AGENT_TEAM_QUICKSTART.md) - 快速开始
- 📄 [AGENT_TEAM_SPAWN_PROMPTS.md](AGENT_TEAM_SPAWN_PROMPTS.md) - 工作指南 (核心文档)
- 📄 [AGENT_TEAM_COORDINATION.md](AGENT_TEAM_COORDINATION.md) - 协调指南
- 📄 [AGENT_TEAM_TASK_TRACKER.md](AGENT_TEAM_TASK_TRACKER.md) - 任务追踪

### 项目文件
- 📁 `D:\ai_work\stock_test\` - 项目根目录
- 📄 `strategy_config.json` - 配置文件
- 📄 `config.py` - 参数定义
- 📄 `backtest_engine.py` - 回测引擎
- 🌐 `templates/index_with_cache.html` - 前端界面
- 🐍 `app_with_cache.py` - Flask应用

---

## 💬 沟通和支持

### 日常沟通
- **进度汇报**: 每日工作结束时更新 TASK_TRACKER.md
- **问题通知**: 遇到问题立即通知相关团队
- **完成通知**: 完成某项任务立即通知

### 寻求帮助
1. 查看对应的 SPAWN_PROMPTS.md 详细指南
2. 查看代码中的注释和文档
3. 查看 COORDINATION.md 中的常见问题
4. 通知相关团队寻求支持

### 问题升级
如果遇到阻塞问题：
1. 详细记录问题描述
2. 通知相关团队
3. 标记优先级 (低/中/高)
4. 跟踪问题解决进展

---

## 🎯 成功标志

项目成功的标志是：

```
☑ 所有4个参数可在Web界面配置
☑ 参数正确传递到回测引擎
☑ 回测结果准确反映参数影响
☑ 所有测试通过 (100% pass rate)
☑ 没有已知BUG
☑ 代码质量达标
☑ 文档完整清晰
☑ 团队协作顺畅
☑ 按时完成 (Day 5前)
```

完成所有项目后：

```
1. 更新 TASK_TRACKER.md 标记所有任务为完成
2. 生成最终报告
3. 代码提交
4. 项目总结
```

---

## ⚠️ 风险预警

### 可能的风险

| 风险 | 可能性 | 影响 | 缓解 |
|------|--------|------|------|
| 参数设计遗漏 | 中 | 高 | config-manager 与他人评审 |
| 计算公式错误 | 低 | 高 | qa-tester 严格验证 |
| 前端验证不完整 | 中 | 中 | 前后端双层验证 |
| 集成问题 | 中 | 中 | 尽早进行集成测试 |
| 时间超期 | 低 | 中 | 并行开发+清晰任务分解 |

### 应对措施

1. **代码冲突**: 严格按照文件所有权规则
2. **理解偏差**: 及时沟通确认需求
3. **进度延误**: 定期汇报进度，早期识别问题
4. **BUG遗漏**: 多轮测试，逐步改进

---

## 📝 文档清单

项目包含以下文档：

```
✓ AGENT_TEAM_README.md (项目总览)
✓ AGENT_TEAM_QUICKSTART.md (快速开始)
✓ AGENT_TEAM_SPAWN_PROMPTS.md (工作指南 - 核心)
✓ AGENT_TEAM_COORDINATION.md (协调指南)
✓ AGENT_TEAM_TASK_TRACKER.md (任务追踪)
✓ PROJECT_LAUNCH_GUIDE.md (启动指南 - 本文件)
```

**总计**: 6份文档，约2500行，涵盖项目全生命周期

---

## 🎉 最后的话

这个项目是关于**系统性地组织多个Agent的协作**。通过清晰的：
- ✓ 角色定义
- ✓ 任务分解
- ✓ 依赖管理
- ✓ 沟通协议
- ✓ 文档支持

我们能够确保高效的协作和高质量的交付。

**现在就开始吧!**

---

## 🚀 行动清单 (今天就做)

- [ ] 阅读本文件 (15分钟)
- [ ] 打开 AGENT_TEAM_QUICKSTART.md 选择你的角色 (10分钟)
- [ ] 打开对应的 SPAWN_PROMPTS.md 详细部分 (30分钟)
- [ ] 启动你的任务工作 (开始编码/测试)
- [ ] 每日工作结束更新 TASK_TRACKER.md

---

**项目启动**: 2026-02-24
**项目路径**: `D:\ai_work\stock_test`
**项目编码**: STOCK-BACKTEST-V3
**团队规模**: 4个Agent
**预计周期**: 4-5个工作日

**祝你工作顺利!** 🚀

