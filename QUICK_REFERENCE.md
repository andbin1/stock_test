# 交易记录功能 - 快速参考指南

## 一行命令启动
```bash
cd "D:\ai_work\stock_test" && python app_with_cache.py
```

## 访问地址
```
http://localhost:5000
```

---

## 页面功能对照表

| 位置 | 功能 | 说明 |
|------|------|------|
| 回测标签页 | 交易记录表格 | 显示前20条交易记录 |
| 回测标签页 | 导出Excel按钮 | 点击下载完整交易明细 |
| 统计卡片 | 交易笔数/总收益率/胜率 | 回测总体指标 |

---

## 新增API端点

### POST /api/backtest/export-trades
**功能**: 导出交易记录到Excel

**请求体**:
```json
{
  "symbols": ["000001", "600000"]
}
```

**响应**: Excel文件下载流

---

## Excel文件结构

### Sheet1: 汇总对比
所有股票的统计对比（交易数、总收益率、胜率等）

### Sheet2+: 股票明细
每只股票一个Sheet，包含所有交易记录：
- 序号
- 买入日期
- 买入价
- 卖出日期
- 卖出价
- 持有天数
- 收益率%（带颜色标记）
- 状态

---

## 核心代码位置

| 功能 | 文件 | 位置 |
|------|------|------|
| 导出API | app_with_cache.py | 行649-719 |
| 交易记录表格 | index_with_cache.html | 行582-625 |
| 导出函数 | index_with_cache.html | 行970-1003 |
| Excel生成 | export_to_excel.py | 行214-297 |

---

## 测试命令

### 测试Excel导出
```bash
cd "D:\ai_work\stock_test"
python test_excel_export.py
```

### 验证语法
```bash
cd "D:\ai_work\stock_test"
python -m py_compile app_with_cache.py
python -m py_compile test_excel_export.py
```

---

## 常见问题

### Q: 点击导出按钮无反应？
A: 打开浏览器控制台(F12)查看错误信息

### Q: Excel文件为空？
A: 检查是否有交易记录，确认回测已成功运行

### Q: 导出时间太长？
A: 减少股票数量，或等待后台处理完成

---

## 关键文件列表

```
D:\ai_work\stock_test\
├── app_with_cache.py                 ← 后端API（已修改）
├── templates\
│   └── index_with_cache.html         ← 前端页面（已修改）
├── export_to_excel.py                ← Excel导出模块（已存在）
├── test_excel_export.py              ← 测试脚本（新创建）
├── TRADE_RECORDS_FEATURE.md          ← 实现文档（新创建）
├── VERIFICATION_CHECKLIST.md         ← 验证清单（新创建）
└── QUICK_REFERENCE.md                ← 快速参考（本文件）
```

---

## 修改摘要

### 后端 (app_with_cache.py)
- 新增 `/api/backtest/export-trades` 端点
- 集成现有导出函数
- 支持文件下载

### 前端 (index_with_cache.html)
- 交易记录表格增加字段（序号、买入价、卖出价）
- 新增"导出完整Excel"按钮
- 实现 `exportToExcel()` 函数
- 添加 `currentBacktestSymbols` 全局变量

---

## 数据流示意

```
[用户点击回测]
       ↓
[回测API返回前20条]
       ↓
[页面显示交易记录]
       ↓
[用户点击导出Excel]
       ↓
[调用导出API]
       ↓
[后端生成Excel]
       ↓
[浏览器下载文件]
```

---

## 版本信息

- **版本**: V2.2
- **日期**: 2026-02-20
- **状态**: 代码已完成
- **待办**: 用户功能测试

---

## 联系支持

如遇问题，请查看:
1. `TRADE_RECORDS_FEATURE.md` - 详细实现文档
2. `VERIFICATION_CHECKLIST.md` - 验证清单
3. 浏览器控制台错误信息

---

## 下一步

1. 启动应用: `python app_with_cache.py`
2. 访问页面: `http://localhost:5000`
3. 运行回测并测试导出功能
4. 查看Excel文件验证数据正确性
