# 测试套件说明

## 快速开始

### 安装依赖

```bash
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行并生成覆盖率报告
pytest --cov=. --cov-report=html tests/

# 查看HTML覆盖率报告
# 打开 htmlcov/index.html
```

## 测试文件结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest配置和共享fixtures
├── test_backtest_engine.py  # 回测引擎测试 (20个测试)
├── test_indicators.py       # 技术指标测试 (39个测试)
├── test_strategy.py         # 交易策略测试 (33个测试)
├── test_data_manager.py     # 数据管理测试 (25个测试)
├── test_data_fetcher.py     # 数据获取测试 (18个测试)
├── test_integration.py      # 集成测试 (12个测试)
├── TEST_REPORT.md          # 详细测试报告
└── README.md               # 本文件
```

## 测试覆盖率摘要

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| indicators.py | 100% | ✅ 优秀 |
| backtest_engine.py | 79% | ✅ 良好 |
| data_manager.py | 77% | ✅ 良好 |
| data_fetcher.py | 79% | ✅ 良好 |
| strategy.py | 64% | ⚠️ 需改进 |
| **核心模块平均** | **83%** | ✅ **达标** |

## 常用命令

```bash
# 运行指定模块测试
pytest tests/test_backtest_engine.py

# 运行指定测试类
pytest tests/test_backtest_engine.py::TestRunSingleStock

# 只运行集成测试
pytest -m integration tests/

# 跳过慢速测试
pytest -m "not slow" tests/

# 详细输出
pytest -v tests/

# 失败时停止
pytest -x tests/

# 并行运行测试 (需要pytest-xdist)
pytest -n auto tests/
```

## 测试分类

- **单元测试**: 测试单个函数/类的功能
- **集成测试**: 测试模块间的交互
- **边界测试**: 测试异常情况和边界条件

## Fixtures说明

在`conftest.py`中定义了以下fixtures：

- `sample_stock_data`: 完整的股票数据 (250天)
- `sample_stock_data_short`: 短期数据 (30天)
- `sample_stock_data_with_signals`: 带明确信号的数据
- `sample_empty_dataframe`: 空DataFrame
- `sample_strategy_params`: 量能突破策略参数
- `sample_steady_trend_params`: 稳健型策略参数
- `sample_aggressive_momentum_params`: 激进型策略参数
- `sample_balanced_multi_factor_params`: 平衡型策略参数
- `sample_trades`: 示例交易记录
- `sample_multiple_stocks_data`: 多只股票数据
- `temp_data_manager`: 临时数据管理器 (用于测试)

## 已知问题

1. **Bug #1**: `backtest_engine.py:124` - 除零保护返回NaN (1个测试失败)
   - 影响: 所有亏损回测的profit_factor显示为NaN
   - 优先级: High
   - 建议修复: 检查wins为空的情况

## 开发建议

### 添加新测试

1. 在对应的`test_*.py`文件中添加测试函数
2. 使用`test_<function>_<scenario>_<expected>`命名规范
3. 使用conftest.py中的fixtures减少重复代码

### 测试最佳实践

- 每个测试只测试一个功能点
- 使用Mock避免真实API调用
- 测试正常流程和边界情况
- 添加清晰的docstring说明测试目的

### 提升覆盖率

当前未覆盖的主要代码：
- 主程序入口 (`__main__`) - 可忽略
- 部分异常处理路径 - 需要增加测试
- 策略深度路径 - 需要更多场景测试

## 持续集成

建议配置CI/CD自动运行测试：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 联系方式

如有问题，请查看 `TEST_REPORT.md` 获取详细信息。
