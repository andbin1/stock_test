# AGENT TEAM 四人协作项目 - 文档索引

**项目名称**: 股票回测系统新功能开发 (4项参数配置)
**启动时间**: 2026-02-24
**项目路径**: `D:\ai_work\stock_test`
**项目状态**: 🔵 准备中

---

## 📚 文档导航 (按阅读顺序)

### 1️⃣ PROJECT_LAUNCH_GUIDE.md (必读)
- **用途**: 项目启动指南
- **内容**: 快速概览和启动检查清单
- **适合**: 项目管理者、团队协调者
- **阅读时间**: 15分钟
- **关键信息**:
  - 项目使命和需求
  - 4个阶段流程
  - 启动前检查清单
  - 快速启动步骤

### 2️⃣ AGENT_TEAM_README.md (必读)
- **用途**: 项目总览和快速参考
- **内容**: 4个团队角色、关键公式、API速查
- **适合**: 所有成员
- **阅读时间**: 15分钟
- **关键信息**:
  - 项目目标和成果
  - 团队角色详细说明
  - 关键公式速查表
  - API接口说明
  - 文件所有权矩阵

### 3️⃣ AGENT_TEAM_QUICKSTART.md (推荐)
- **用途**: 5分钟快速入门指南
- **内容**: 选择角色、快速任务清单、速查表
- **适合**: 快速上手的开发者
- **阅读时间**: 10分钟
- **关键信息**:
  - 5分钟一句话总结
  - 4个角色的快速导航
  - 总体流程图
  - 快速公式和API查询

### 4️⃣ AGENT_TEAM_SPAWN_PROMPTS.md (核心文件)
- **用途**: 4个团队的详细工作指南
- **内容**:
  - 团队1️⃣ 配置管理员 - 配置参数结构设计
  - 团队2️⃣ 回测引擎开发者 - 交易成本计算实现
  - 团队3️⃣ 前端UI开发者 - 参数配置界面实现
  - 团队4️⃣ 测试验证员 - 集成和单元测试编写
- **适合**: 各团队成员按职责阅读
- **阅读时间**: 60分钟
- **每个团队约**: 70-110行详细指南

### 5️⃣ AGENT_TEAM_COORDINATION.md (参考)
- **用途**: 项目协调和管理指南
- **内容**:
  - 项目架构和技术栈
  - 执行阶段详细说明
  - 团队沟通协议
  - 文件所有权管理
  - 风险和缓解措施
- **适合**: 需要了解全局的人员
- **阅读时间**: 30分钟

### 6️⃣ AGENT_TEAM_TASK_TRACKER.md (实时)
- **用途**: 任务管理和进度追踪
- **内容**:
  - 4个主任务和子任务清单
  - 依赖关系图
  - 时间线
  - 每日进度更新模板
  - 进度指标和KPI
- **适合**: 项目跟踪和每日汇报
- **阅读时间**: 20分钟

---

## 👥 团队角色快速导航

### 如果你是 "配置管理员 (config-manager)"

**快速路径**:
1. PROJECT_LAUNCH_GUIDE.md (5分钟)
2. AGENT_TEAM_QUICKSTART.md - 找到你的部分 (5分钟)
3. AGENT_TEAM_SPAWN_PROMPTS.md - **团队1️⃣** 部分 (30分钟)

**你的任务**:
- 修改 strategy_config.json (新增4个参数)
- 修改 config.py (新增常量和验证函数，+30行)
- 修改 app_with_cache.py (新增2个API端点，+40行)
- 测试并通知其他团队

**预计时间**: 2-3小时
**优先级**: ⭐⭐⭐ 最高 (其他团队都依赖你!)

---

### 如果你是 "回测引擎开发者 (backtest-engine-dev)"

**快速路径**:
1. PROJECT_LAUNCH_GUIDE.md (5分钟)
2. 等待 config-manager 完成
3. AGENT_TEAM_QUICKSTART.md - 找到你的部分 (5分钟)
4. AGENT_TEAM_SPAWN_PROMPTS.md - **团队2️⃣** 部分 (30分钟)

**你的任务**:
- 更新 BacktestEngine 类接受新参数
- 实现4个新方法 (position_size, slippage, cost等)
- 更新 run_single_stock() 应用新计算
- 测试并通知 qa-tester

**预计时间**: 3-4小时
**优先级**: ⭐⭐⭐ 最高
**前置条件**: ⚠️ 等待 config-manager 完成

---

### 如果你是 "前端UI开发者 (frontend-developer)"

**快速路径**:
1. PROJECT_LAUNCH_GUIDE.md (5分钟)
2. 等待 config-manager 完成
3. AGENT_TEAM_QUICKSTART.md - 找到你的部分 (5分钟)
4. AGENT_TEAM_SPAWN_PROMPTS.md - **团队3️⃣** 部分 (30分钟)

**你的任务**:
- 添加配置面板HTML (初始资金、占比、手续费、滑点)
- 添加CSS样式
- 实现JavaScript交互逻辑 (加载、保存、验证)
- 集成到回测流程，测试并通知 qa-tester

**预计时间**: 3-4小时
**优先级**: ⭐⭐⭐ 最高
**前置条件**: ⚠️ 等待 config-manager 完成

---

### 如果你是 "测试验证员 (qa-tester)"

**快速路径**:
1. PROJECT_LAUNCH_GUIDE.md (5分钟)
2. 等待其他3个团队完成
3. AGENT_TEAM_QUICKSTART.md - 找到你的部分 (5分钟)
4. AGENT_TEAM_SPAWN_PROMPTS.md - **团队4️⃣** 部分 (30分钟)

**你的任务**:
- 创建单元测试 (参数验证、计算函数、极端情况)
- 创建集成测试 (API、端到端流程)
- 运行所有测试并记录结果
- 生成测试报告，报告任何问题

**预计时间**: 3-4小时
**优先级**: ⭐⭐⭐ 最高
**前置条件**: ⚠️ 等待其他3个团队完成

---

## 📊 关键指标速查

### 4个参数范围
```
初始资金 (initial_capital):    10k ~ 10M 元 (默认100k)
交易占比 (position_ratio):     1% ~ 99% (默认20%)
手续费 (commission_rate):       0% ~ 100% (默认0.1%)
滑点 (slippage):               0% ~ 5% (默认0%)
```

### 关键公式
```
position_size = floor(initial_capital * position_ratio / price)
buy_price = original_price * (1 + slippage)
sell_price = original_price * (1 - slippage)
trade_cost = amount * commission_rate
```

### API端点
```
GET /api/backtest/settings (获取配置)
POST /api/backtest/settings (更新配置)
```

### 文件变更
```
strategy_config.json (修改，新增参数)
config.py (修改，+30行)
backtest_engine.py (修改，+150行)
templates/index_with_cache.html (修改，+400行)
app_with_cache.py (修改，+40行API部分)
tests/test_backtest_new_features.py (新建，300+行)
test_config_flow.py (新建，100+行)
```

---

## 📋 工作流程 (4个阶段)

### 🟢 阶段1: 配置设计 (Day 1)
- **Leader**: config-manager
- **Duration**: 2-3小时
- **Status**: 准备中
- **Blocking**: 所有其他团队

### 🟡 阶段2: 并行实现 (Day 2-3)
- **Leaders**: backtest-engine-dev + frontend-developer (并行)
- **Duration**: 6-8小时
- **Status**: 待启动
- **Blocking**: qa-tester

### 🔵 阶段3: 集成测试 (Day 4)
- **Leader**: qa-tester
- **Duration**: 3-4小时
- **Status**: 待启动
- **Outputs**: TEST_REPORT.md

### 🟣 阶段4: 反馈修改 (Day 5)
- **All Teams**
- **Duration**: 1-2小时
- **Status**: 待启动
- **Result**: 项目完成 ✓

---

## ✅ 启动前检查清单

### 环境准备
- [ ] Python 3.7+ 已安装
- [ ] Flask 已安装
- [ ] Pytest 已安装
- [ ] 项目目录可读写

### 文档准备
- [ ] 所有6份文档已查看
- [ ] 文档索引已理解
- [ ] 推荐路径已确认

### 人员准备
- [ ] 4个团队成员已分配
- [ ] 角色职责已明确
- [ ] 沟通方式已确认

---

## 🚀 立即开始

### 第一步: 阅读启动指南 (5分钟)
→ 打开 **PROJECT_LAUNCH_GUIDE.md**

### 第二步: 选择你的角色 (5分钟)
→ 打开 **AGENT_TEAM_QUICKSTART.md** 并找到你的部分

### 第三步: 精读工作指南 (30分钟)
→ 打开 **AGENT_TEAM_SPAWN_PROMPTS.md** 对应团队部分

### 第四步: 开始工作!
→ 按照指南逐步执行你的任务

---

## 📞 文档查询

### 我需要快速了解
→ 打开 **AGENT_TEAM_README.md** (15分钟)

### 我需要立即开始
→ 打开 **AGENT_TEAM_QUICKSTART.md** (10分钟)

### 我需要详细指南
→ 打开 **AGENT_TEAM_SPAWN_PROMPTS.md** 对应部分 (30分钟)

### 我需要理解全景
→ 打开 **AGENT_TEAM_COORDINATION.md** (30分钟)

### 我需要追踪进度
→ 打开 **AGENT_TEAM_TASK_TRACKER.md** (持续更新)

### 我需要了解启动
→ 打开 **PROJECT_LAUNCH_GUIDE.md** (15分钟)

---

## 📄 文档清单

| 文档 | 目的 | 大小 | 优先级 |
|------|------|------|--------|
| PROJECT_LAUNCH_GUIDE.md | 项目启动指南 | 5页 | ⭐⭐⭐ |
| AGENT_TEAM_README.md | 项目总览 | 4页 | ⭐⭐⭐ |
| AGENT_TEAM_QUICKSTART.md | 快速开始 | 3页 | ⭐⭐ |
| AGENT_TEAM_SPAWN_PROMPTS.md | 工作指南 | 12页 | ⭐⭐⭐⭐⭐ |
| AGENT_TEAM_COORDINATION.md | 协调指南 | 8页 | ⭐⭐ |
| AGENT_TEAM_TASK_TRACKER.md | 任务追踪 | 6页 | ⭐⭐ |
| AGENT_TEAM_INDEX.md | 文档索引 | 本文件 | ⭐ |

**总计**: 7份文档，约41页，~2500行

---

## 💡 推荐阅读顺序

### 对于快速行动的人
1. AGENT_TEAM_QUICKSTART.md (10分钟)
2. AGENT_TEAM_SPAWN_PROMPTS.md 对应部分 (30分钟)
3. 开始工作!

### 对于喜欢了解全景的人
1. PROJECT_LAUNCH_GUIDE.md (15分钟)
2. AGENT_TEAM_README.md (15分钟)
3. AGENT_TEAM_COORDINATION.md (30分钟)
4. AGENT_TEAM_SPAWN_PROMPTS.md 对应部分 (30分钟)
5. 开始工作!

### 对于项目管理者
1. PROJECT_LAUNCH_GUIDE.md (15分钟)
2. AGENT_TEAM_COORDINATION.md (30分钟)
3. AGENT_TEAM_TASK_TRACKER.md (20分钟)
4. 日常追踪进度

---

## 🎓 按角色推荐阅读

### Config-Manager 推荐路径 (1小时)
```
1. PROJECT_LAUNCH_GUIDE.md (15分钟)
   ↓ 了解项目全景
2. AGENT_TEAM_README.md (15分钟)
   ↓ 理解参数定义
3. AGENT_TEAM_SPAWN_PROMPTS.md - 团队1️⃣ (30分钟)
   ↓ 精读详细指南
4. 开始工作! (2-3小时)
```

### Backtest-Engine-Dev 推荐路径 (1小时)
```
1. PROJECT_LAUNCH_GUIDE.md (15分钟)
   ↓ 了解项目全景
2. AGENT_TEAM_README.md - 关键公式部分 (10分钟)
   ↓ 理解计算公式
3. 等待 config-manager 完成...
4. AGENT_TEAM_SPAWN_PROMPTS.md - 团队2️⃣ (30分钟)
   ↓ 精读详细指南
5. 开始工作! (3-4小时)
```

### Frontend-Developer 推荐路径 (1小时)
```
1. PROJECT_LAUNCH_GUIDE.md (15分钟)
   ↓ 了解项目全景
2. AGENT_TEAM_README.md - API部分 (10分钟)
   ↓ 理解API接口
3. 等待 config-manager 完成...
4. AGENT_TEAM_SPAWN_PROMPTS.md - 团队3️⃣ (30分钟)
   ↓ 精读详细指南
5. 开始工作! (3-4小时)
```

### QA-Tester 推荐路径 (1小时)
```
1. PROJECT_LAUNCH_GUIDE.md (15分钟)
   ↓ 了解项目全景
2. AGENT_TEAM_README.md - 验收标准部分 (10分钟)
   ↓ 理解测试要求
3. 等待其他团队完成...
4. AGENT_TEAM_SPAWN_PROMPTS.md - 团队4️⃣ (30分钟)
   ↓ 精读详细指南
5. 开始工作! (3-4小时)
```

---

## 🎯 核心资源速查

### 需要快速查询参数范围?
→ 查看 **AGENT_TEAM_README.md** 的参数表
→ 查看 **AGENT_TEAM_QUICKSTART.md** 的速查表

### 需要查看API格式?
→ 查看 **AGENT_TEAM_README.md** 的API部分
→ 查看 **AGENT_TEAM_QUICKSTART.md** 的API速查

### 需要理解计算公式?
→ 查看 **AGENT_TEAM_README.md** 的公式部分
→ 查看 **AGENT_TEAM_QUICKSTART.md** 的公式速查

### 需要了解文件所有权?
→ 查看 **AGENT_TEAM_README.md** 的所有权矩阵
→ 查看 **AGENT_TEAM_COORDINATION.md** 的冲突预防

### 需要了解工作流程?
→ 查看 **PROJECT_LAUNCH_GUIDE.md** 的阶段说明
→ 查看 **AGENT_TEAM_COORDINATION.md** 的执行流程

### 需要追踪进度?
→ 打开 **AGENT_TEAM_TASK_TRACKER.md** 并更新

---

## 🌟 最后的话

这个项目的成功依赖于：
- ✓ 清晰的文档
- ✓ 明确的任务分工
- ✓ 及时的沟通
- ✓ 高质量的执行
- ✓ 完善的测试

所有这些都已为你准备好了。

**现在就开始吧!** 🚀

---

**项目启动**: 2026-02-24
**项目路径**: `D:\ai_work\stock_test`
**最后更新**: 2026-02-24

