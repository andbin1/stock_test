# 测试指南

本指南帮助开发者快速上手项目的测试框架。

---

## 🚀 快速开始

### 1. 安装测试依赖

```bash
cd D:\ai_work\stock_test
pip install -r requirements-dev.txt
```

### 2. 运行所有测试

```bash
pytest tests/
```

### 3. 查看覆盖率

```bash
pytest --cov=. --cov-report=html tests/
```

然后打开 `htmlcov/index.html` 查看详细报告。

---

## 📊 测试结果概览

### 当前测试状态

```
测试用例总数: 135
通过: 133
失败: 2
覆盖率 (核心模块): 83%
```

### 模块覆盖率

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| indicators.py | 100% | ✅ |
| backtest_engine.py | 79% | ✅ |
| data_manager.py | 77% | ✅ |
| data_fetcher.py | 79% | ✅ |
| strategy.py | 64% | ⚠️ |

---

## 🧪 测试命令速查

### 基础命令

```bash
# 运行所有测试
pytest tests/

# 运行单个文件
pytest tests/test_backtest_engine.py

# 运行单个测试类
pytest tests/test_backtest_engine.py::TestRunSingleStock

# 运行单个测试函数
pytest tests/test_backtest_engine.py::TestRunSingleStock::test_run_single_stock_no_trades
```

### 详细输出

```bash
# 显示详细信息
pytest -v tests/

# 显示print输出
pytest -s tests/

# 显示完整错误堆栈
pytest --tb=long tests/

# 失败时立即停止
pytest -x tests/
```

### 覆盖率测试

```bash
# 生成HTML报告
pytest --cov=. --cov-report=html tests/

# 终端显示覆盖率
pytest --cov=. --cov-report=term tests/

# 显示未覆盖代码行号
pytest --cov=. --cov-report=term-missing tests/

# 只测试核心模块
pytest --cov=backtest_engine --cov=indicators --cov=strategy tests/
```

### 筛选测试

```bash
# 按标记运行
pytest -m integration tests/     # 只运行集成测试
pytest -m "not slow" tests/      # 跳过慢速测试

# 按名称模糊匹配
pytest -k "backtest" tests/      # 运行名称包含backtest的测试
pytest -k "not slow" tests/      # 跳过名称包含slow的测试
```

### 调试

```bash
# 在失败处进入调试器
pytest --pdb tests/

# 显示最慢的10个测试
pytest --durations=10 tests/

# 只运行上次失败的测试
pytest --lf tests/

# 先运行上次失败的，再运行其他
pytest --ff tests/
```

---

## 📁 测试文件结构

```
tests/
├── conftest.py               # 共享fixtures和配置
├── test_backtest_engine.py   # 回测引擎测试
├── test_indicators.py        # 技术指标测试
├── test_strategy.py          # 交易策略测试
├── test_data_manager.py      # 数据管理测试
├── test_data_fetcher.py      # 数据获取测试
├── test_integration.py       # 集成测试
├── TEST_REPORT.md           # 详细测试报告
├── BUGS_FOUND.md            # 发现的Bug列表
└── README.md                # 测试说明
```

---

## 🔧 编写新测试

### 1. 选择合适的文件

- 测试indicators.py → 编辑 `tests/test_indicators.py`
- 测试strategy.py → 编辑 `tests/test_strategy.py`
- 测试新模块 → 创建 `tests/test_<module>.py`

### 2. 使用fixtures

```python
def test_my_function(sample_stock_data):
    """测试描述"""
    # 使用conftest.py中定义的fixture
    df = sample_stock_data
    # ... 测试代码
```

### 3. 命名规范

```python
# 函数命名: test_<function>_<scenario>_<expected>
def test_calculate_ma_basic():
    """测试基本的MA计算"""
    pass

def test_calculate_ma_empty_data():
    """测试空数据"""
    pass

def test_calculate_ma_with_nan_values():
    """测试包含NaN值的数据"""
    pass
```

### 4. 使用Mock

```python
from unittest.mock import patch

@patch('data_fetcher.get_stock_data')
def test_fetch_with_mock(mock_get_stock_data, sample_stock_data):
    """使用Mock避免真实API调用"""
    mock_get_stock_data.return_value = sample_stock_data

    # 测试代码
    result = some_function()

    # 验证Mock被调用
    mock_get_stock_data.assert_called_once()
```

### 5. 测试断言

```python
import pytest

# 基本断言
assert result == expected
assert len(trades) > 0
assert 'MA5' in df.columns

# 浮点数比较
assert result == pytest.approx(10.5, rel=1e-5)

# 异常测试
with pytest.raises(ValueError):
    some_function_that_should_raise()

# 警告测试
with pytest.warns(UserWarning):
    some_function_that_warns()
```

---

## 🐛 已知问题

### Bug #1: 除零保护返回NaN

**位置**: `backtest_engine.py:124`
**状态**: 未修复
**影响**: 全亏损回测profit_factor显示NaN

运行测试时会看到：
```
FAILED tests/test_backtest_engine.py::TestEdgeCases::test_divide_by_zero_protection
```

### Bug #2: 移动止盈逻辑

**位置**: `strategy.py:222-223`
**状态**: 待确认
**影响**: 测试假设可能不正确

运行测试时会看到：
```
FAILED tests/test_strategy.py::TestSteadyTrendStrategy::test_get_trades_trailing_stop
```

详细信息见: `tests/BUGS_FOUND.md`

---

## 📈 提升覆盖率

### 当前未覆盖的代码

#### strategy.py (需要提升)

**未覆盖代码行**:
- 65-66, 81-83: 买入信号判断分支
- 86-105: 卖出信号计算
- 109-113: 未平仓头寸处理边界情况

**建议增加测试**:
```python
def test_volume_breakout_multiple_trades_cycle():
    """测试多次买卖循环"""
    pass

def test_volume_breakout_edge_case_last_day_buy():
    """测试最后一天买入的情况"""
    pass
```

#### data_manager.py

**未覆盖代码**: 主要是命令行工具 (341-397行)

**建议**:
- 如果CLI不是核心功能，可以标记为跳过
- 或创建专门的CLI测试

---

## 🎯 测试最佳实践

### 1. 测试隔离

每个测试应该独立，不依赖其他测试：

```python
# ❌ 错误 - 依赖全局状态
global_data = None

def test_setup():
    global global_data
    global_data = fetch_data()

def test_process():
    result = process(global_data)  # 依赖前一个测试

# ✅ 正确 - 使用fixture
@pytest.fixture
def test_data():
    return fetch_data()

def test_process(test_data):
    result = process(test_data)
```

### 2. 使用参数化测试

避免重复代码：

```python
@pytest.mark.parametrize("period,expected", [
    (5, "MA5"),
    (10, "MA10"),
    (20, "MA20"),
])
def test_ma_column_names(sample_stock_data, period, expected):
    df = add_indicators(sample_stock_data, ma_periods=[period])
    assert expected in df.columns
```

### 3. 测试边界条件

```python
def test_function():
    # 正常情况
    assert func(10) == expected_normal

    # 边界情况
    assert func(0) == expected_zero
    assert func(-1) == expected_negative
    assert func(999999) == expected_large

    # 异常情况
    with pytest.raises(ValueError):
        func(None)
```

### 4. 清晰的错误信息

```python
# ❌ 不好
assert len(trades) > 0

# ✅ 好
assert len(trades) > 0, f"Expected at least 1 trade, got {len(trades)}"
```

---

## 🔄 持续集成

### GitHub Actions配置

创建 `.github/workflows/test.yml`:

```yaml
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

---

## 📚 参考资源

### pytest文档
- [pytest官方文档](https://docs.pytest.org/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)

### 项目文档
- `tests/TEST_REPORT.md` - 详细测试报告
- `tests/BUGS_FOUND.md` - Bug列表
- `tests/README.md` - 测试套件说明

---

## 💡 常见问题

### Q: 测试运行很慢怎么办？

A: 使用pytest-xdist并行运行：
```bash
pip install pytest-xdist
pytest -n auto tests/
```

### Q: 如何只运行失败的测试？

A: 使用--lf参数：
```bash
pytest --lf tests/
```

### Q: 如何查看具体哪些代码未覆盖？

A: 使用--cov-report=term-missing：
```bash
pytest --cov=. --cov-report=term-missing tests/
```

### Q: 如何在测试中打印调试信息？

A: 使用-s参数显示print输出：
```bash
pytest -s tests/test_backtest_engine.py
```

### Q: 测试中需要真实数据怎么办？

A: 使用Mock或fixtures：
```python
@patch('module.get_real_data')
def test_with_mock(mock_get_data):
    mock_get_data.return_value = test_data
    # 测试代码
```

---

## 📞 获取帮助

1. 查看 `tests/TEST_REPORT.md` 了解详细测试结果
2. 查看 `tests/BUGS_FOUND.md` 了解已知问题
3. 查看 `tests/README.md` 了解测试结构
4. 运行 `pytest --help` 查看所有命令选项

---

**最后更新**: 2026-02-16
**维护者**: AI Test Engineer
