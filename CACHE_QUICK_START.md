# ⚡ 本地缓存系统 - 快速启动（5分钟）

## 🎯 核心特性

✅ 获取真实数据一次，永久保存本地
✅ 离线回测（无需连接网络）
✅ 手动更新数据（增量更新）
✅ Web界面管理数据

---

## 🚀 3分钟快速开始

### 步骤1：获取数据（首次）

```bash
# 获取单只股票 (000001)
python data_manager.py fetch 000001

# 或批量获取20只股票
python fetch_data_batch.py
```

**输出示例**：
```
⏳ 000001: 正在从网络获取数据...
✓ 000001: 已保存 25 条数据到本地缓存
```

### 步骤2：离线回测

```bash
# 使用本地缓存数据进行回测
python backtest_with_cache.py
```

**输出示例**：
```
========== 回测结果 ==========
  • 有效股票数: 1
  • 总交易数: 2
  • 总收益: +5.12%
  • 平均单笔收益: +2.56%
  • 胜率: 100.0%
```

### 步骤3：更新数据

```bash
# 增量更新 (只获取新数据)
python data_manager.py update 000001
```

---

## 📋 命令参考

| 命令 | 说明 |
|------|------|
| `python data_manager.py status` | 查看缓存状态 |
| `python data_manager.py fetch <code>` | 获取单只股票 |
| `python data_manager.py update <code>` | 增量更新 |
| `python data_manager.py export <code>` | 导出为CSV |
| `python data_manager.py clear [code]` | 清空缓存 |
| `python fetch_data_batch.py` | 批量获取20只 |
| `python backtest_with_cache.py` | 使用缓存回测 |

---

## 🌐 Web界面 (推荐)

```bash
# 启动Web应用
python app_with_cache.py

# 打开浏览器: http://localhost:5000
```

**功能**：
- 📥 获取数据
- 🔄 更新数据
- 🔢 批量获取
- 🔄 回测
- 📊 状态管理

---

## 💡 使用示例

### 例1：快速验证策略

```bash
# 1. 获取单只股票
python data_manager.py fetch 000001

# 2. 使用缓存进行回测
python backtest_with_cache.py

# 3. 修改参数后再回测 (无需重新获取数据!)
# 编辑 config.py 中的 STRATEGY_PARAMS
python backtest_with_cache.py
```

### 例2：每周更新所有股票

```bash
# 更新多只股票
python data_manager.py update 000001
python data_manager.py update 600000
python data_manager.py update 000858

# 进行回测
python backtest_with_cache.py
```

### 例3：导出数据用于分析

```bash
# 导出为CSV
python data_manager.py export 000001

# 用Excel或Python分析
# data_export/000001_data.csv
```

---

## 📊 缓存状态检查

```bash
python data_manager.py status
```

**输出**：
```
总数据量: 25 条
数据库文件: ./data_cache/stock_data.db
数据库大小: 0.02 MB

更新日志:
  000001: 25条 (最后更新: 2025-02-13T14:30:00)
```

---

## 🔄 数据更新流程

```
首次获取 (5-10秒/只)
    ↓
保存到本地数据库 (永久存储)
    ↓
后续使用缓存 (<100ms)
    ↓
需要新数据时，增量更新 (只下载新数据)
```

---

## 🎯 场景对应

| 场景 | 操作 |
|------|------|
| 首次获取数据 | `python data_manager.py fetch <code>` |
| 参数调优 | 修改config.py + `python backtest_with_cache.py` |
| 每天更新 | `python data_manager.py update <code>` |
| 批量回测 | `python backtest_with_cache.py` |
| 查看数据 | `python data_manager.py export <code>` |
| 清理缓存 | `python data_manager.py clear <code>` |

---

## ✅ 已验证

```
✓ 数据库初始化成功
✓ 数据获取并缓存成功 (000001: 25条数据)
✓ 缓存查询正常
✓ 回测引擎兼容缓存数据
```

---

## 🎓 下一步

1. **获取数据**
   ```bash
   python fetch_data_batch.py  # 获取20只股票
   ```

2. **运行回测**
   ```bash
   python backtest_with_cache.py
   ```

3. **查看报告**
   - 回测汇总_中证500.csv
   - 详细交易_中证500.csv
   - 回测报告_中证500_*.xlsx

4. **持续优化**
   - 修改 config.py 中的参数
   - 重新运行回测（数据无需重新获取！）
   - 对比结果

---

## 📞 常见问题

**Q: 数据保存在哪？**
A: `./data_cache/stock_data.db`

**Q: 可以离线使用吗？**
A: 可以，数据已保存本地

**Q: 多久更新一次？**
A: 您决定，可以每天、每周或按需更新

**Q: 数据准确吗？**
A: 来自efinance/akshare，与网站数据一致

---

## 🏁 总结

| 传统方式 | 新方式 |
|----------|--------|
| 每次回测都连网 | 一次获取，永久使用 |
| 网络不稳定 | 完全离线 |
| 参数对比慢 | 秒级回测 |
| 无法共享数据 | 数据库可共享 |

**现在开始**：
```bash
python fetch_data_batch.py
python backtest_with_cache.py
```

🎉 完成！
