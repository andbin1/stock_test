# 🚀 Agent Team 四人协作项目 - 从这里开始

**项目启动**: 2026-02-24
**项目路径**: `D:\ai_work\stock_test`

---

## ⚡ 5秒快速概览

这是一个**4个Agent协作**的项目，目标是为股票回测系统添加**4项参数配置**：
1. 初始金额
2. 交易占比
3. 手续费
4. 滑点

**8份文档 + 4个工作任务** 已为你准备好。

---

## 🎯 第一步: 了解你的角色

你是以下哪一个?

### 我是 **配置管理员** (config-manager)
👉 **立即打开**: `AGENT_TEAM_QUICKSTART.md` (找到你的部分)
- **任务**: 设计配置参数系统 (3个文件修改)
- **时间**: 2-3小时
- **优先级**: ⭐⭐⭐ 最高 (其他人都等你!)

### 我是 **回测引擎开发者** (backtest-engine-dev)
👉 **等待**: config-manager 完成
👉 **然后打开**: `AGENT_TEAM_QUICKSTART.md` (找到你的部分)
- **任务**: 实现成本计算逻辑 (1个文件修改)
- **时间**: 3-4小时
- **优先级**: ⭐⭐⭐ 最高

### 我是 **前端UI开发者** (frontend-developer)
👉 **等待**: config-manager 完成
👉 **然后打开**: `AGENT_TEAM_QUICKSTART.md` (找到你的部分)
- **任务**: 创建参数配置界面 (1个文件修改)
- **时间**: 3-4小时
- **优先级**: ⭐⭐⭐ 最高

### 我是 **测试验证员** (qa-tester)
👉 **等待**: 其他3个团队完成
👉 **然后打开**: `AGENT_TEAM_QUICKSTART.md` (找到你的部分)
- **任务**: 编写测试和验证 (3个文件创建)
- **时间**: 3-4小时
- **优先级**: ⭐⭐⭐ 最高

---

## 📚 文档导航

### 🔥 如果你要快速开始 (15分钟)
```
1. 本文件 (00_START_HERE.md) ← 你正在读
2. AGENT_TEAM_QUICKSTART.md (找到你的角色)
3. AGENT_TEAM_SPAWN_PROMPTS.md (你的详细指南)
然后: 开始工作!
```

### 📖 如果你要全面了解 (90分钟)
```
1. PROJECT_LAUNCH_GUIDE.md (项目启动)
2. AGENT_TEAM_README.md (项目总览)
3. AGENT_TEAM_COORDINATION.md (全局架构)
4. AGENT_TEAM_SPAWN_PROMPTS.md (详细指南)
然后: 开始工作!
```

### 📋 如果你要追踪进度 (实时)
```
使用: AGENT_TEAM_TASK_TRACKER.md
- 查看任务进度
- 每日更新状态
- 报告问题
```

### 🔍 如果你要快速查询
```
使用: AGENT_TEAM_INDEX.md
- 快速导航到任何部分
- 速查表
- 关键公式
```

---

## 📂 核心文件清单

| 文件 | 用途 | 优先级 |
|------|------|--------|
| **00_START_HERE.md** | 本文件，快速入门 | ⭐⭐⭐ |
| **PROJECT_LAUNCH_GUIDE.md** | 项目启动指南 | ⭐⭐⭐ |
| **AGENT_TEAM_README.md** | 项目总览 | ⭐⭐⭐ |
| **AGENT_TEAM_QUICKSTART.md** | 快速开始 | ⭐⭐⭐ |
| **AGENT_TEAM_SPAWN_PROMPTS.md** | 详细工作指南 (核心) | ⭐⭐⭐⭐⭐ |
| **AGENT_TEAM_COORDINATION.md** | 协调指南 | ⭐⭐ |
| **AGENT_TEAM_TASK_TRACKER.md** | 任务追踪 | ⭐⭐ |
| **AGENT_TEAM_INDEX.md** | 文档索引 | ⭐ |
| **AGENT_TEAM_DELIVERY_SUMMARY.md** | 交付总结 | ⭐ |

**总计**: 9份文档，7000+行

---

## ⚡ 快速行动清单 (现在就做)

### 第1步: 了解项目 (5分钟)
- [ ] 阅读本文件 (00_START_HERE.md)
- [ ] 知道你的角色是什么

### 第2步: 选择路径 (5分钟)
- [ ] 快速开始? → 打开 AGENT_TEAM_QUICKSTART.md
- [ ] 全面了解? → 打开 PROJECT_LAUNCH_GUIDE.md
- [ ] 查询参考? → 打开 AGENT_TEAM_INDEX.md

### 第3步: 精读指南 (30分钟)
- [ ] 打开对应的 AGENT_TEAM_SPAWN_PROMPTS.md 部分
- [ ] 仔细阅读你的任务说明
- [ ] 理解所有验收标准

### 第4步: 开始工作! (开始编码/测试)
- [ ] 按照指南逐步执行
- [ ] 如有疑问查阅文档
- [ ] 完成后通知相关团队

---

## 📊 关键数据快查

### 4个参数
```
初始金额:     10k ~ 10M 元 (默认100k)
交易占比:     1% ~ 99% (默认20%)
手续费:       0% ~ 100% (默认0.1%)
滑点:         0% ~ 5% (默认0%)
```

### 3个关键公式
```
持仓数量 = floor(初始资金 * 占比 / 股价)
买入价 = 原价 * (1 + 滑点)
卖出价 = 原价 * (1 - 滑点)
```

### 2个API端点
```
GET  /api/backtest/settings (获取配置)
POST /api/backtest/settings (更新配置)
```

---

## ⏰ 4个工作阶段

### 🟢 阶段1: 配置设计 (Day 1)
```
config-manager 启动
  ↓ 2-3小时
3个文件修改 + API实现
  ↓ 完成后通知其他团队
```

### 🟡 阶段2: 并行实现 (Day 2-3)
```
backtest-engine-dev 启动          frontend-developer 启动
  ↓ 并行 3-4小时                     ↓ 并行 3-4小时
回测引擎更新                        前端UI实现
  ↓ 完成后都通知qa-tester          ↓
```

### 🔵 阶段3: 集成测试 (Day 4)
```
qa-tester 启动
  ↓ 3-4小时
单元测试 + 集成测试 + 手动测试
  ↓ 生成测试报告
发现问题? → 反馈给相关团队
```

### 🟣 阶段4: 反馈修改 (Day 5)
```
相关团队修复问题
  ↓ 1-2小时
qa-tester 重新验证
  ↓ 所有通过!
项目完成 ✓
```

---

## 🎯 项目成功标志

项目完成时，应该满足:

```
✓ 所有4个参数可在Web界面配置
✓ 参数正确保存和读取
✓ 回测引擎应用参数
✓ 结果反映参数影响
✓ 所有单元测试通过 (100%)
✓ 所有集成测试通过 (100%)
✓ 代码无语法错误
✓ 文档完整清晰
✓ 没有关键BUG
✓ 按时完成 (Day 5前)
```

---

## 💡 关键提示

### ⚠️ 顺序很重要
- config-manager **必须**先启动 (阻塞所有人)
- 其他人才能依次启动
- 不要跳过任何阶段

### 💬 沟通很重要
- 完成后立即通知相关人员
- 遇到问题立即报告
- 定期更新进度

### ✨ 质量很重要
- 宁可慢一点，也要准确
- 所有测试都要通过
- 代码要有注释

### 📖 文档是最好的帮助
- 遇到问题先查文档
- 多读 AGENT_TEAM_SPAWN_PROMPTS.md
- 参考 AGENT_TEAM_README.md 快速查询

---

## 🔗 下一步

### 立即点击打开以下文件:

**1️⃣ 快速开始** (推荐)
→ [`AGENT_TEAM_QUICKSTART.md`](AGENT_TEAM_QUICKSTART.md)
- 5分钟选择你的角色
- 10分钟了解快速任务

**2️⃣ 详细指南** (核心)
→ [`AGENT_TEAM_SPAWN_PROMPTS.md`](AGENT_TEAM_SPAWN_PROMPTS.md)
- 找到对应的团队部分 (1️⃣-4️⃣)
- 30分钟精读详细指南

**3️⃣ 其他参考** (按需)
- [`PROJECT_LAUNCH_GUIDE.md`](PROJECT_LAUNCH_GUIDE.md) - 项目启动指南
- [`AGENT_TEAM_README.md`](AGENT_TEAM_README.md) - 项目总览
- [`AGENT_TEAM_COORDINATION.md`](AGENT_TEAM_COORDINATION.md) - 协调指南
- [`AGENT_TEAM_TASK_TRACKER.md`](AGENT_TEAM_TASK_TRACKER.md) - 任务追踪
- [`AGENT_TEAM_INDEX.md`](AGENT_TEAM_INDEX.md) - 文档索引

---

## ❓ 常见问题

### Q: 我应该先读什么?
**A**: 打开 `AGENT_TEAM_QUICKSTART.md` (10分钟)

### Q: 我需要做什么?
**A**: 找到你的角色，打开对应的 `AGENT_TEAM_SPAWN_PROMPTS.md` 部分

### Q: 我应该花多长时间?
**A**: 总共4-5个工作日，每个人3-4小时

### Q: 如果我遇到问题?
**A**:
1. 查看 `AGENT_TEAM_SPAWN_PROMPTS.md` 的详细说明
2. 查看代码中的现有注释
3. 通知相关团队

### Q: 完成后应该做什么?
**A**: 更新 `AGENT_TEAM_TASK_TRACKER.md` 并通知下一个团队

---

## 📞 快速联系

### 遇到问题?
1. 查看对应文档
2. 检查现有代码
3. 向相关团队发出通知

### 需要帮助?
- 配置参数 → config-manager
- 计算逻辑 → backtest-engine-dev
- 界面问题 → frontend-developer
- 测试问题 → qa-tester

### 需要协调?
- 查看 `AGENT_TEAM_COORDINATION.md`
- 更新 `AGENT_TEAM_TASK_TRACKER.md`
- 发送进度汇报

---

## 🎉 最后的话

这是一个**组织有序、文档完善、流程清晰**的项目。

你已经拥有了所有需要的信息。现在只需要：

1. **选择你的角色** (现在就在上面选)
2. **打开对应的指南** (下面的链接)
3. **按照指南工作** (逐步执行)
4. **完成时通知他人** (协作成功)

---

## 🚀 立即开始

**第一步**: 选择你的角色 (在上面已列出)

**第二步**: 打开对应的文件:
- [`AGENT_TEAM_QUICKSTART.md`](AGENT_TEAM_QUICKSTART.md) ← **先读这个** (10分钟)
- [`AGENT_TEAM_SPAWN_PROMPTS.md`](AGENT_TEAM_SPAWN_PROMPTS.md) ← **然后读这个** (30分钟)

**第三步**: 开始工作! 🎯

---

**祝你工作顺利!** 🚀

---

**项目信息**
- 项目名: 股票回测系统新功能开发
- 启动时间: 2026-02-24
- 项目路径: `D:\ai_work\stock_test`
- 预计周期: 4-5个工作日
- 文档完整度: 100%

