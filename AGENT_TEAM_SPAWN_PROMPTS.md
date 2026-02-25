# Agent Team 四人协作 - Spawn Prompts

## 项目概览

股票回测系统新功能开发：添加初始金额、交易占比、手续费、滑点四项可配置参数。

**项目路径**: `D:\ai_work\stock_test`
**总体目标**: 使用户能在Web界面配置这4个参数，并让回测引擎精确计算成本

---

## 团队1️⃣: 配置管理员 (config-manager)

### 角色描述
负责系统配置的设计和管理，确保参数定义清晰、验证规则完整、API接口标准。

### 直接职责

#### 任务1.1: 修改 strategy_config.json
在 `D:\ai_work\stock_test\strategy_config.json` 中添加全局交易配置：

```json
{
  "current_strategy": "grid_trading",
  "trading_settings": {
    "initial_capital": 100000,
    "position_ratio": 0.2,
    "commission_rate": 0.001,
    "slippage": 0.0
  },
  "params": { ... }
}
```

**验收标准**:
- ✓ 文件有效的JSON格式
- ✓ 4个参数都有默认值
- ✓ 参数注释清晰说明含义和范围

#### 任务1.2: 在 config.py 添加常量和验证函数
在 `D:\ai_work\stock_test\config.py` 的第266行后添加：

```python
# 交易设置参数（新增）
INITIAL_CAPITAL_DEFAULT = 100000      # 初始资金10万元
INITIAL_CAPITAL_MIN = 10000           # 最低10万元
INITIAL_CAPITAL_MAX = 10000000        # 最高1000万元

POSITION_RATIO_DEFAULT = 0.2          # 单笔占比1/5
POSITION_RATIO_MIN = 0.01             # 最低1%
POSITION_RATIO_MAX = 0.99             # 最高99%

COMMISSION_RATE_DEFAULT = 0.001       # 手续费0.1%（万1）
COMMISSION_RATE_MIN = 0               # 最低无手续费
COMMISSION_RATE_MAX = 0.05            # 最高5%手续费

SLIPPAGE_DEFAULT = 0.0                # 滑点0%
SLIPPAGE_MIN = 0                      # 最低0%
SLIPPAGE_MAX = 0.05                   # 最高5%滑点

# 参数验证函数
def validate_trading_settings(settings: dict) -> tuple[bool, str]:
    """验证交易设置参数的有效性

    Args:
        settings: {'initial_capital': float, 'position_ratio': float, 'commission_rate': float, 'slippage': float}

    Returns:
        (is_valid: bool, error_message: str)
    """
    # 验证初始金额
    if 'initial_capital' in settings:
        ic = settings['initial_capital']
        if not (INITIAL_CAPITAL_MIN <= ic <= INITIAL_CAPITAL_MAX):
            return False, f"初始金额必须在 {INITIAL_CAPITAL_MIN} 到 {INITIAL_CAPITAL_MAX} 之间"

    # 验证交易占比
    if 'position_ratio' in settings:
        pr = settings['position_ratio']
        if not (POSITION_RATIO_MIN <= pr <= POSITION_RATIO_MAX):
            return False, f"交易占比必须在 {POSITION_RATIO_MIN} 到 {POSITION_RATIO_MAX} 之间"

    # 验证手续费
    if 'commission_rate' in settings:
        cr = settings['commission_rate']
        if not (COMMISSION_RATE_MIN <= cr <= COMMISSION_RATE_MAX):
            return False, f"手续费必须在 {COMMISSION_RATE_MIN} 到 {COMMISSION_RATE_MAX} 之间"

    # 验证滑点
    if 'slippage' in settings:
        sp = settings['slippage']
        if not (SLIPPAGE_MIN <= sp <= SLIPPAGE_MAX):
            return False, f"滑点必须在 {SLIPPAGE_MIN} 到 {SLIPPAGE_MAX} 之间"

    return True, ""

def get_default_trading_settings() -> dict:
    """获取默认交易设置"""
    return {
        'initial_capital': INITIAL_CAPITAL_DEFAULT,
        'position_ratio': POSITION_RATIO_DEFAULT,
        'commission_rate': COMMISSION_RATE_DEFAULT,
        'slippage': SLIPPAGE_DEFAULT,
    }
```

**验收标准**:
- ✓ 所有常量都有恰当的命名和注释
- ✓ validate_trading_settings 函数能正确验证所有4个参数
- ✓ 没有语法错误，可正确import

#### 任务1.3: 在 app_with_cache.py 添加API端点
在 `D:\ai_work\stock_test\app_with_cache.py` 中添加两个新端点（在第741行前）：

```python
@app.route('/api/backtest/settings', methods=['GET'])
def get_backtest_settings():
    """获取当前回测配置（初始资金、交易占比、手续费、滑点）"""
    try:
        settings = config_manager.get_trading_settings()
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backtest/settings', methods=['POST'])
def update_backtest_settings():
    """更新回测配置"""
    try:
        data = request.json
        new_settings = {
            'initial_capital': data.get('initial_capital'),
            'position_ratio': data.get('position_ratio'),
            'commission_rate': data.get('commission_rate'),
            'slippage': data.get('slippage'),
        }

        # 验证参数
        from config import validate_trading_settings
        is_valid, error_msg = validate_trading_settings(new_settings)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400

        # 更新配置
        config_manager.update_trading_settings(new_settings)
        return jsonify({
            'success': True,
            'message': '配置已更新',
            'settings': config_manager.get_trading_settings()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**验收标准**:
- ✓ GET端点能返回当前配置
- ✓ POST端点能更新配置并验证
- ✓ 两个端点都有错误处理
- ✓ 与ConfigManager集成正确

### 与其他团队的通讯要点

完成后需要通知：
- **backtest-engine-dev**: 告知新的参数结构和API端点定义
  - 参数结构：`{'initial_capital': float, 'position_ratio': float, 'commission_rate': float, 'slippage': float}`
  - API获取参数的方式：调用 `/api/backtest/settings` GET端点

- **frontend-developer**: 告知新的API端点和参数验证规则
  - GET `/api/backtest/settings` 返回格式
  - POST `/api/backtest/settings` 的请求格式和可能的错误码

### 文件所有权
- `strategy_config.json` ✓
- `config.py` ✓ (仅新增代码段)
- `app_with_cache.py` ✓ (仅两个新API端点)

### 完成检查清单
- [ ] strategy_config.json 有效且包含4个新参数
- [ ] config.py 中常量和验证函数无语法错误
- [ ] 两个API端点已添加到app_with_cache.py
- [ ] 通知其他两个开发团队
- [ ] 参数定义文档已准备好供后续团队参考

---

## 团队2️⃣: 回测引擎开发者 (backtest-engine-dev)

### 角色描述
负责回测逻辑的实现和交易成本精确计算，确保手续费和滑点正确应用。

### 直接职责

#### 任务2.1: 理解参数结构（由config-manager提供）

从配置管理员获得的参数结构：
```python
{
    'initial_capital': 100000,      # 初始资金（元）
    'position_ratio': 0.2,          # 单笔交易占比（0-1）
    'commission_rate': 0.001,       # 手续费率（0-1）
    'slippage': 0.0                 # 滑点（0-1）
}
```

关键公式需要实现的：
1. **持仓数量计算**: `position_size = floor(initial_capital * position_ratio / current_price)`
2. **买入价格**: `buy_price = open_price * (1 + slippage)`
3. **卖出价格**: `sell_price = open_price * (1 - slippage)`
4. **交易成本**: `cost = trade_amount * commission_rate`

#### 任务2.2: 更新 backtest_engine.py

修改 `D:\ai_work\stock_test\backtest_engine.py` 中的 `BacktestEngine` 类和 `run_single_stock` 方法：

```python
class BacktestEngine:
    """回测引擎 - 执行回测并计算绩效指标"""

    def __init__(self, initial_capital: float = None, position_ratio: float = None,
                 commission_rate: float = None, slippage: float = None):
        """初始化回测引擎

        Args:
            initial_capital: 初始资金（元），默认从config.py读取
            position_ratio: 单笔交易占比，默认从config.py读取
            commission_rate: 手续费率，默认从config.py读取
            slippage: 滑点，默认从config.py读取
        """
        from config import (
            INITIAL_CAPITAL_DEFAULT, POSITION_RATIO_DEFAULT,
            COMMISSION_RATE_DEFAULT, SLIPPAGE_DEFAULT
        )

        self.initial_capital = initial_capital or INITIAL_CAPITAL_DEFAULT
        self.position_ratio = position_ratio or POSITION_RATIO_DEFAULT
        self.commission_rate = commission_rate or COMMISSION_RATE_DEFAULT
        self.slippage = slippage or SLIPPAGE_DEFAULT

    def calculate_position_size(self, price: float) -> int:
        """根据当前价格计算持仓数量

        Args:
            price: 当前股价

        Returns:
            持仓数量（手数*100）
        """
        if price <= 0:
            return 0
        amount = self.initial_capital * self.position_ratio / price
        return int(amount // 100) * 100  # 按手计算（100股/手）

    def apply_slippage_to_price(self, price: float, is_buy: bool) -> float:
        """应用滑点到价格

        Args:
            price: 原始价格
            is_buy: True表示买入，False表示卖出

        Returns:
            应用滑点后的价格
        """
        if is_buy:
            return price * (1 + self.slippage)
        else:
            return price * (1 - self.slippage)

    def calculate_trade_cost(self, amount: float) -> float:
        """计算交易成本（手续费）

        Args:
            amount: 交易金额

        Returns:
            交易成本
        """
        return amount * self.commission_rate

    def run_single_stock(self, symbol: str, df: pd.DataFrame, strategy: Any) -> dict:
        """对单只股票运行回测（更新版本）

        参数和返回值保持不变，但内部实现需要应用新的成本计算
        """
        trades = strategy.get_trades(df)

        if not trades:
            return {
                'symbol': symbol,
                'trades': [],
                'total_return': 0,
                'num_trades': 0,
                'win_rate': 0,
                'avg_return': 0,
                'max_loss': 0,
                'profit_factor': 0,
                'backtest_settings': {
                    'initial_capital': self.initial_capital,
                    'position_ratio': self.position_ratio,
                    'commission_rate': self.commission_rate,
                    'slippage': self.slippage,
                }
            }

        # 对每笔交易应用滑点和手续费
        processed_trades = []
        for trade in trades:
            # 重新计算价格（应用滑点）
            buy_price_with_slip = self.apply_slippage_to_price(trade['买入价'], is_buy=True)
            sell_price_with_slip = self.apply_slippage_to_price(trade['卖出价'], is_buy=False)

            # 计算持仓数量
            position_size = self.calculate_position_size(buy_price_with_slip)

            # 计算交易金额和成本
            buy_amount = buy_price_with_slip * position_size
            sell_amount = sell_price_with_slip * position_size
            buy_cost = self.calculate_trade_cost(buy_amount)
            sell_cost = self.calculate_trade_cost(sell_amount)

            # 重新计算收益率
            total_cost = buy_amount + buy_cost + sell_cost
            profit = sell_amount - buy_amount - buy_cost - sell_cost
            return_rate = (profit / total_cost) * 100 if total_cost > 0 else 0

            processed_trade = trade.copy()
            processed_trade['买入价'] = buy_price_with_slip
            processed_trade['卖出价'] = sell_price_with_slip
            processed_trade['持仓数量'] = position_size
            processed_trade['买入成本'] = buy_cost
            processed_trade['卖出成本'] = sell_cost
            processed_trade['收益率%'] = return_rate
            processed_trades.append(processed_trade)

        # 后续统计逻辑保持不变
        trades_df = pd.DataFrame(processed_trades)
        total_return = trades_df['收益率%'].sum()
        num_trades = len(processed_trades)
        wins = len(trades_df[trades_df['收益率%'] > 0])
        losses = len(trades_df[trades_df['收益率%'] <= 0])
        win_rate = wins / num_trades * 100 if num_trades > 0 else 0

        avg_profit = trades_df[trades_df['收益率%'] > 0]['收益率%'].mean() if wins > 0 else 0
        avg_loss = abs(trades_df[trades_df['收益率%'] <= 0]['收益率%'].mean()) if losses > 0 else 0
        profit_factor = avg_profit / avg_loss if avg_loss > 0 else (1 if avg_profit > 0 else 0)
        max_loss = trades_df['收益率%'].min() if len(trades_df) > 0 else 0

        return {
            'symbol': symbol,
            'trades': processed_trades,
            'total_return': total_return,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_return': trades_df['收益率%'].mean(),
            'max_loss': max_loss,
            'profit_factor': profit_factor,
            'trades_df': trades_df,
            'backtest_settings': {
                'initial_capital': self.initial_capital,
                'position_ratio': self.position_ratio,
                'commission_rate': self.commission_rate,
                'slippage': self.slippage,
            }
        }
```

**验收标准**:
- ✓ 4个新的参数可正确初始化
- ✓ position_size 计算公式正确
- ✓ 滑点应用逻辑正确（买入+，卖出-）
- ✓ 手续费计算正确
- ✓ 没有语法错误

#### 任务2.3: 集成到回测流程

确保在调用 `run_single_stock` 和 `run_multiple_stocks` 时，能正确传入这些参数：

```python
# 从配置中读取参数
from config_manager import ConfigManager
config_mgr = ConfigManager()
settings = config_mgr.get_trading_settings()

# 创建引擎实例时传入参数
engine = BacktestEngine(
    initial_capital=settings['initial_capital'],
    position_ratio=settings['position_ratio'],
    commission_rate=settings['commission_rate'],
    slippage=settings['slippage']
)

# 执行回测
results = engine.run_multiple_stocks(stocks_data, strategy)
```

### 与其他团队的通讯要点

完成后需要通知：
- **qa-tester**: 告知新的计算方法和需要测试的公式
  - position_size = floor(初始资金 * 占比 / 价格)
  - 买入价 = 原价 * (1 + 滑点)
  - 卖出价 = 原价 * (1 - 滑点)
  - 成本 = 金额 * 手续费率

- **frontend-developer**: 告知回测结果中包含的新字段
  - 每笔交易记录中包含 `买入成本`, `卖出成本`, `持仓数量`
  - 回测结果中包含 `backtest_settings` 配置信息

### 文件所有权
- `backtest_engine.py` ✓
- `strategy.py` (仅查看，不修改)

### 完成检查清单
- [ ] BacktestEngine.__init__() 接受4个新参数
- [ ] 4个新方法/函数已实现（calculate_position_size, apply_slippage_to_price, calculate_trade_cost）
- [ ] run_single_stock 已更新使用新的成本计算
- [ ] 回测结果包含 backtest_settings 信息
- [ ] 代码无语法错误，能正确执行
- [ ] 通知qa-tester新的计算公式
- [ ] 通知frontend-developer新的结果字段

---

## 团队3️⃣: 前端UI开发者 (frontend-developer)

### 角色描述
负责用户界面设计和参数输入表单，使用户能轻松配置交易参数。

### 直接职责

#### 任务3.1: 理解API接口（由config-manager提供）

获取的API接口：
```
GET /api/backtest/settings
  返回: {"success": true, "settings": {
    "initial_capital": 100000,
    "position_ratio": 0.2,
    "commission_rate": 0.001,
    "slippage": 0.0
  }}

POST /api/backtest/settings
  请求: {
    "initial_capital": 100000,
    "position_ratio": 0.2,
    "commission_rate": 0.001,
    "slippage": 0.0
  }
  返回: {"success": true, "message": "配置已更新", "settings": {...}}
```

#### 任务3.2: 在 templates/index_with_cache.html 添加配置面板

在 `D:\ai_work\stock_test\templates\index_with_cache.html` 中添加新的HTML section：

```html
<!-- 交易配置面板 -->
<div class="section trading-settings-section">
    <h3 class="section-title">交易配置</h3>

    <!-- 初始资金配置 -->
    <div class="input-group">
        <label for="initialCapital">初始资金 (元)</label>
        <div class="input-wrapper">
            <input type="number" id="initialCapital" name="initialCapital"
                   min="10000" max="10000000" value="100000" step="10000">
            <span class="input-hint">范围: 10,000 ~ 10,000,000</span>
        </div>
    </div>

    <!-- 交易占比配置 -->
    <div class="input-group">
        <label for="positionRatio">单笔交易占比</label>
        <div class="input-wrapper">
            <select id="positionRatioSelect" name="positionRatioSelect">
                <option value="0.333">1/3 (33.3%)</option>
                <option value="0.2" selected>1/5 (20%)</option>
                <option value="0.1">1/10 (10%)</option>
                <option value="custom">自定义</option>
            </select>
            <input type="number" id="positionRatioCustom" name="positionRatioCustom"
                   min="0.01" max="0.99" value="0.2" step="0.01" style="display:none;">
            <span class="input-hint">建议: 1/3、1/5、1/10 或自定义 (1%-99%)</span>
        </div>
    </div>

    <!-- 手续费配置 -->
    <div class="input-group">
        <label for="commissionRate">手续费率 (%)</label>
        <div class="input-wrapper">
            <input type="number" id="commissionRate" name="commissionRate"
                   min="0" max="100" value="0.1" step="0.01">
            <span class="input-hint">范围: 0% ~ 100%，默认0.1% (万1)</span>
        </div>
    </div>

    <!-- 滑点配置 -->
    <div class="input-group">
        <label for="slippage">滑点 (%)</label>
        <div class="input-wrapper">
            <input type="number" id="slippage" name="slippage"
                   min="0" max="5" value="0" step="0.01">
            <span class="input-hint">范围: 0% ~ 5%，0表示无滑点</span>
        </div>
    </div>

    <!-- 配置预览 -->
    <div class="config-preview">
        <div class="preview-item">
            <span class="preview-label">初始资金:</span>
            <span class="preview-value" id="previewCapital">¥100,000</span>
        </div>
        <div class="preview-item">
            <span class="preview-label">单笔交易额:</span>
            <span class="preview-value" id="previewTradeAmount">¥20,000</span>
        </div>
        <div class="preview-item">
            <span class="preview-label">手续费:</span>
            <span class="preview-value" id="previewCommission">0.1%</span>
        </div>
        <div class="preview-item">
            <span class="preview-label">滑点:</span>
            <span class="preview-value" id="previewSlippage">0%</span>
        </div>
    </div>

    <!-- 保存配置按钮 -->
    <button id="saveSettingsBtn" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
        保存配置
    </button>
</div>
```

#### 任务3.3: 添加CSS样式

在 HTML 的 `<style>` 部分添加：

```css
/* 交易配置相关样式 */
.trading-settings-section {
    background: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    border-left: 4px solid #667eea;
}

.trading-settings-section .input-wrapper {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.trading-settings-section input,
.trading-settings-section select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.3s;
}

.trading-settings-section input:focus,
.trading-settings-section select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-hint {
    font-size: 12px;
    color: #999;
    display: block;
    margin-top: 4px;
}

.config-preview {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 12px;
    margin: 15px 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.preview-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: #f5f5f5;
    border-radius: 4px;
}

.preview-label {
    font-size: 12px;
    color: #666;
    font-weight: 500;
}

.preview-value {
    font-size: 14px;
    color: #333;
    font-weight: bold;
}
```

#### 任务3.4: 添加JavaScript交互逻辑

在 HTML 的 `<script>` 部分添加：

```javascript
// 交易配置管理
const TradingSettingsManager = {
    // 初始化配置
    init() {
        this.loadSettings();
        this.attachEventListeners();
    },

    // 从服务器加载配置
    loadSettings() {
        fetch('/api/backtest/settings')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.settings) {
                    document.getElementById('initialCapital').value = data.settings.initial_capital;
                    document.getElementById('positionRatioSelect').value = data.settings.position_ratio;
                    document.getElementById('commissionRate').value = (data.settings.commission_rate * 100).toFixed(2);
                    document.getElementById('slippage').value = (data.settings.slippage * 100).toFixed(2);
                    this.updatePreview();
                }
            })
            .catch(err => console.error('加载配置失败:', err));
    },

    // 绑定事件监听器
    attachEventListeners() {
        // 初始资金变化时更新预览
        document.getElementById('initialCapital').addEventListener('change', () => this.updatePreview());

        // 交易占比下拉框变化处理
        document.getElementById('positionRatioSelect').addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                document.getElementById('positionRatioCustom').style.display = 'block';
            } else {
                document.getElementById('positionRatioCustom').style.display = 'none';
                document.getElementById('positionRatioCustom').value = e.target.value;
            }
            this.updatePreview();
        });

        // 自定义交易占比变化时更新预览
        document.getElementById('positionRatioCustom').addEventListener('change', () => this.updatePreview());

        // 手续费变化时更新预览
        document.getElementById('commissionRate').addEventListener('change', () => this.updatePreview());

        // 滑点变化时更新预览
        document.getElementById('slippage').addEventListener('change', () => this.updatePreview());

        // 保存配置按钮
        document.getElementById('saveSettingsBtn').addEventListener('click', () => this.saveSettings());
    },

    // 获取当前表单值
    getFormValues() {
        const initialCapital = parseFloat(document.getElementById('initialCapital').value) || 100000;
        const positionRatioSelect = document.getElementById('positionRatioSelect').value;
        const positionRatio = positionRatioSelect === 'custom'
            ? parseFloat(document.getElementById('positionRatioCustom').value) || 0.2
            : parseFloat(positionRatioSelect);
        const commissionRate = parseFloat(document.getElementById('commissionRate').value) || 0.1;
        const slippage = parseFloat(document.getElementById('slippage').value) || 0;

        return { initialCapital, positionRatio, commissionRate, slippage };
    },

    // 验证参数
    validate(values) {
        const errors = [];

        if (values.initialCapital < 10000 || values.initialCapital > 10000000) {
            errors.push('初始资金必须在 10,000 ~ 10,000,000 之间');
        }
        if (values.positionRatio <= 0 || values.positionRatio >= 1) {
            errors.push('交易占比必须在 0% ~ 100% 之间');
        }
        if (values.commissionRate < 0 || values.commissionRate > 100) {
            errors.push('手续费必须在 0% ~ 100% 之间');
        }
        if (values.slippage < 0 || values.slippage > 5) {
            errors.push('滑点必须在 0% ~ 5% 之间');
        }

        return { isValid: errors.length === 0, errors };
    },

    // 更新预览
    updatePreview() {
        const { initialCapital, positionRatio, commissionRate, slippage } = this.getFormValues();

        // 更新初始资金预览
        document.getElementById('previewCapital').textContent = '¥' + initialCapital.toLocaleString();

        // 更新单笔交易额预览
        const tradeAmount = initialCapital * positionRatio;
        document.getElementById('previewTradeAmount').textContent = '¥' + Math.floor(tradeAmount).toLocaleString();

        // 更新手续费预览
        document.getElementById('previewCommission').textContent = commissionRate.toFixed(2) + '%';

        // 更新滑点预览
        document.getElementById('previewSlippage').textContent = slippage.toFixed(2) + '%';
    },

    // 保存配置到服务器
    saveSettings() {
        const { initialCapital, positionRatio, commissionRate, slippage } = this.getFormValues();

        // 验证
        const validation = this.validate({ initialCapital, positionRatio, commissionRate, slippage });
        if (!validation.isValid) {
            alert('配置验证失败:\n' + validation.errors.join('\n'));
            return;
        }

        // 保存
        fetch('/api/backtest/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                initial_capital: initialCapital,
                position_ratio: positionRatio,
                commission_rate: commissionRate / 100,  // 转换为小数
                slippage: slippage / 100                 // 转换为小数
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('配置已保存!');
                this.updatePreview();
            } else {
                alert('保存失败: ' + (data.error || '未知错误'));
            }
        })
        .catch(err => {
            console.error('保存配置错误:', err);
            alert('保存配置失败，请检查网络连接');
        });
    }
};

// 页面加载完毕后初始化
document.addEventListener('DOMContentLoaded', () => {
    TradingSettingsManager.init();
});
```

#### 任务3.5: 集成到回测参数提交流程

修改现有的回测参数提交逻辑，确保包含这些新参数：

```javascript
// 在回测参数提交前获取交易配置
async function submitBacktest() {
    // ... 现有的参数收集逻辑 ...

    // 获取交易配置
    const { initialCapital, positionRatio, commissionRate, slippage } =
        TradingSettingsManager.getFormValues();

    // 合并到回测参数中
    const backtestParams = {
        // ... 现有参数 ...
        initial_capital: initialCapital,
        position_ratio: positionRatio,
        commission_rate: commissionRate / 100,
        slippage: slippage / 100
    };

    // 提交回测
    // ...
}
```

#### 任务3.6: 在回测结果中显示配置信息

在显示回测结果的地方添加配置信息展示：

```html
<!-- 回测结果配置信息显示 -->
<div class="result-settings-info" style="display: none;">
    <h4>使用的配置参数</h4>
    <div class="settings-info-grid">
        <div class="info-item">
            <span>初始资金:</span>
            <span id="resultInitialCapital">¥100,000</span>
        </div>
        <div class="info-item">
            <span>交易占比:</span>
            <span id="resultPositionRatio">20%</span>
        </div>
        <div class="info-item">
            <span>手续费:</span>
            <span id="resultCommissionRate">0.1%</span>
        </div>
        <div class="info-item">
            <span>滑点:</span>
            <span id="resultSlippage">0%</span>
        </div>
    </div>
</div>
```

### 与其他团队的通讯要点

接收来自：
- **config-manager**: API接口定义和参数验证规则
- **backtest-engine-dev**: 回测结果中包含的新字段信息

### 文件所有权
- `templates/index_with_cache.html` ✓

### 完成检查清单
- [ ] 交易配置面板HTML已添加到页面
- [ ] CSS样式已正确应用
- [ ] JavaScript逻辑已实现（加载、保存、验证、预览）
- [ ] 前端验证规则完整且正确
- [ ] 参数正确集成到回测提交流程
- [ ] 回测结果中显示配置信息
- [ ] 页面无报错，功能正常运行

---

## 团队4️⃣: 测试验证员 (qa-tester)

### 角色描述
负责功能验证、集成测试、确保所有功能正确协作。

### 直接职责

#### 任务4.1: 创建单元测试文件 tests/test_backtest_new_features.py

```python
"""测试回测系统新功能（初始资金、交易占比、手续费、滑点）"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    INITIAL_CAPITAL_DEFAULT, POSITION_RATIO_DEFAULT,
    COMMISSION_RATE_DEFAULT, SLIPPAGE_DEFAULT,
    INITIAL_CAPITAL_MIN, INITIAL_CAPITAL_MAX,
    POSITION_RATIO_MIN, POSITION_RATIO_MAX,
    COMMISSION_RATE_MIN, COMMISSION_RATE_MAX,
    SLIPPAGE_MIN, SLIPPAGE_MAX,
    validate_trading_settings, get_default_trading_settings
)
from backtest_engine import BacktestEngine


class TestParameterValidation:
    """参数验证测试"""

    def test_get_default_settings(self):
        """测试获取默认设置"""
        defaults = get_default_trading_settings()
        assert defaults['initial_capital'] == INITIAL_CAPITAL_DEFAULT
        assert defaults['position_ratio'] == POSITION_RATIO_DEFAULT
        assert defaults['commission_rate'] == COMMISSION_RATE_DEFAULT
        assert defaults['slippage'] == SLIPPAGE_DEFAULT

    def test_validate_initial_capital_valid(self):
        """测试有效的初始资金"""
        settings = {'initial_capital': 100000}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, msg

    def test_validate_initial_capital_too_low(self):
        """测试初始资金过低"""
        settings = {'initial_capital': 5000}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid
        assert "初始金额" in msg

    def test_validate_initial_capital_too_high(self):
        """测试初始资金过高"""
        settings = {'initial_capital': 20000000}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid

    def test_validate_position_ratio_valid(self):
        """测试有效的交易占比"""
        for ratio in [0.1, 0.2, 0.333, 0.5, 0.9]:
            settings = {'position_ratio': ratio}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid, f"ratio={ratio}验证失败: {msg}"

    def test_validate_position_ratio_invalid(self):
        """测试无效的交易占比"""
        invalid_ratios = [0, -0.1, 1.0, 1.5]
        for ratio in invalid_ratios:
            settings = {'position_ratio': ratio}
            is_valid, msg = validate_trading_settings(settings)
            assert not is_valid, f"ratio={ratio}应该验证失败"

    def test_validate_commission_rate_valid(self):
        """测试有效的手续费"""
        for rate in [0, 0.001, 0.01, 0.05]:
            settings = {'commission_rate': rate}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid, f"commission_rate={rate}验证失败"

    def test_validate_commission_rate_invalid(self):
        """测试无效的手续费"""
        invalid_rates = [-0.001, 0.1, 1.0]
        for rate in invalid_rates:
            settings = {'commission_rate': rate}
            is_valid, msg = validate_trading_settings(settings)
            assert not is_valid

    def test_validate_slippage_valid(self):
        """测试有效的滑点"""
        for slip in [0, 0.001, 0.01, 0.05]:
            settings = {'slippage': slip}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid

    def test_validate_slippage_invalid(self):
        """测试无效的滑点"""
        invalid_slips = [-0.001, 0.1, 1.0]
        for slip in invalid_slips:
            settings = {'slippage': slip}
            is_valid, msg = validate_trading_settings(settings)
            assert not is_valid


class TestBacktestEngineCalculations:
    """回测引擎计算测试"""

    def test_engine_initialization_with_defaults(self):
        """测试引擎使用默认参数初始化"""
        engine = BacktestEngine()
        assert engine.initial_capital == INITIAL_CAPITAL_DEFAULT
        assert engine.position_ratio == POSITION_RATIO_DEFAULT
        assert engine.commission_rate == COMMISSION_RATE_DEFAULT
        assert engine.slippage == SLIPPAGE_DEFAULT

    def test_engine_initialization_with_custom_values(self):
        """测试引擎使用自定义参数初始化"""
        engine = BacktestEngine(
            initial_capital=50000,
            position_ratio=0.1,
            commission_rate=0.002,
            slippage=0.01
        )
        assert engine.initial_capital == 50000
        assert engine.position_ratio == 0.1
        assert engine.commission_rate == 0.002
        assert engine.slippage == 0.01

    def test_position_size_calculation(self):
        """测试持仓数量计算"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)
        # 100000 * 0.2 / 20 = 1000, 按手计算 = 1000 (10手)
        position = engine.calculate_position_size(20.0)
        assert position > 0
        # 持仓应该是100的倍数（按手计算）
        assert position % 100 == 0

    def test_position_size_with_different_prices(self):
        """测试不同价格下的持仓数量"""
        engine = BacktestEngine(initial_capital=100000, position_ratio=0.2)

        # 价格越高，持仓数量越少
        pos_high = engine.calculate_position_size(50.0)
        pos_low = engine.calculate_position_size(10.0)
        assert pos_low > pos_high

    def test_slippage_buy_price(self):
        """测试买入滑点应用"""
        engine = BacktestEngine(slippage=0.01)
        original_price = 100.0
        buy_price = engine.apply_slippage_to_price(original_price, is_buy=True)
        assert buy_price == 101.0  # 100 * (1 + 0.01)

    def test_slippage_sell_price(self):
        """测试卖出滑点应用"""
        engine = BacktestEngine(slippage=0.01)
        original_price = 100.0
        sell_price = engine.apply_slippage_to_price(original_price, is_buy=False)
        assert sell_price == 99.0  # 100 * (1 - 0.01)

    def test_trade_cost_calculation(self):
        """测试交易成本计算"""
        engine = BacktestEngine(commission_rate=0.001)
        amount = 100000
        cost = engine.calculate_trade_cost(amount)
        assert cost == 100.0  # 100000 * 0.001

    def test_zero_slippage(self):
        """测试零滑点"""
        engine = BacktestEngine(slippage=0.0)
        price = 100.0
        buy = engine.apply_slippage_to_price(price, is_buy=True)
        sell = engine.apply_slippage_to_price(price, is_buy=False)
        assert buy == price
        assert sell == price


class TestIntegration:
    """集成测试"""

    def test_backtest_with_custom_settings_affects_result(self):
        """测试不同配置对回测结果的影响"""
        # 这个测试需要模拟数据或使用实际数据
        # 验证相同股票、不同配置下的结果差异
        pass

    def test_extreme_case_small_capital(self):
        """测试极端情况：小初始资金"""
        engine = BacktestEngine(initial_capital=10000, position_ratio=0.9)
        position = engine.calculate_position_size(100.0)
        # 应该能计算但数量有限
        assert position >= 0

    def test_extreme_case_high_commission(self):
        """测试极端情况：高手续费"""
        engine = BacktestEngine(commission_rate=0.05)
        cost = engine.calculate_trade_cost(100000)
        assert cost == 5000  # 100000 * 0.05

    def test_extreme_case_large_slippage(self):
        """测试极端情况：大滑点"""
        engine = BacktestEngine(slippage=0.05)
        original = 100.0
        buy = engine.apply_slippage_to_price(original, is_buy=True)
        sell = engine.apply_slippage_to_price(original, is_buy=False)
        assert buy == 105.0
        assert sell == 95.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
```

#### 任务4.2: 创建集成测试脚本 test_config_flow.py

```python
"""集成测试：从API到回测的完整流程"""

import requests
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

class TestConfigFlow:
    """测试配置流程"""

    BASE_URL = "http://localhost:5000"

    def test_get_settings_endpoint(self):
        """测试获取设置端点"""
        print("\n测试: GET /api/backtest/settings")
        response = requests.get(f"{self.BASE_URL}/api/backtest/settings")
        print(f"状态码: {response.status_code}")
        assert response.status_code == 200

        data = response.json()
        print(f"响应: {json.dumps(data, indent=2)}")
        assert data['success'] == True
        assert 'settings' in data
        assert 'initial_capital' in data['settings']
        assert 'position_ratio' in data['settings']
        assert 'commission_rate' in data['settings']
        assert 'slippage' in data['settings']
        print("✓ 获取设置成功")

    def test_update_settings_endpoint_valid(self):
        """测试有效的设置更新"""
        print("\n测试: POST /api/backtest/settings (有效数据)")

        new_settings = {
            "initial_capital": 50000,
            "position_ratio": 0.1,
            "commission_rate": 0.002,
            "slippage": 0.01
        }

        response = requests.post(
            f"{self.BASE_URL}/api/backtest/settings",
            json=new_settings
        )
        print(f"状态码: {response.status_code}")
        assert response.status_code == 200

        data = response.json()
        print(f"响应: {json.dumps(data, indent=2)}")
        assert data['success'] == True
        print("✓ 设置更新成功")

    def test_update_settings_endpoint_invalid(self):
        """测试无效的设置更新"""
        print("\n测试: POST /api/backtest/settings (无效数据)")

        # 初始资金过低
        invalid_settings = {
            "initial_capital": 5000,  # 小于最小值
            "position_ratio": 0.2,
            "commission_rate": 0.001,
            "slippage": 0.0
        }

        response = requests.post(
            f"{self.BASE_URL}/api/backtest/settings",
            json=invalid_settings
        )
        print(f"状态码: {response.status_code}")
        assert response.status_code == 400  # 应该返回400错误

        data = response.json()
        print(f"错误信息: {data['error']}")
        assert data['success'] == False
        print("✓ 无效数据正确拒绝")

    def test_settings_persistence(self):
        """测试设置持久化"""
        print("\n测试: 设置持久化")

        # 设置新值
        test_settings = {
            "initial_capital": 75000,
            "position_ratio": 0.15,
            "commission_rate": 0.0015,
            "slippage": 0.005
        }

        response = requests.post(
            f"{self.BASE_URL}/api/backtest/settings",
            json=test_settings
        )
        assert response.status_code == 200

        # 立即读取验证
        response = requests.get(f"{self.BASE_URL}/api/backtest/settings")
        retrieved = response.json()['settings']

        print(f"设置的值: {test_settings}")
        print(f"读取的值: {retrieved}")
        assert retrieved['initial_capital'] == test_settings['initial_capital']
        assert retrieved['position_ratio'] == test_settings['position_ratio']
        print("✓ 设置成功持久化")

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("配置流程集成测试")
        print("=" * 60)

        try:
            self.test_get_settings_endpoint()
            self.test_update_settings_endpoint_valid()
            self.test_update_settings_endpoint_invalid()
            self.test_settings_persistence()

            print("\n" + "=" * 60)
            print("✓ 所有集成测试通过!")
            print("=" * 60)
            return True
        except AssertionError as e:
            print(f"\n✗ 测试失败: {e}")
            return False
        except requests.exceptions.ConnectionError:
            print("\n✗ 无法连接到服务器，请确保应用正在运行")
            return False


if __name__ == '__main__':
    import time

    # 给服务器启动时间
    print("等待服务器启动...")
    time.sleep(2)

    tester = TestConfigFlow()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
```

#### 任务4.3: 创建验证报告模板 TEST_REPORT_TEMPLATE.md

```markdown
# 回测系统新功能验证报告

## 测试日期
[日期]

## 测试环境
- Python版本: [版本]
- Flask版本: [版本]
- 浏览器: [浏览器]

## 测试范围

### 1. 参数验证
- [ ] 初始资金验证 (10000-10000000)
- [ ] 交易占比验证 (1%-99%)
- [ ] 手续费验证 (0%-100%)
- [ ] 滑点验证 (0%-5%)

### 2. API功能
- [ ] GET /api/backtest/settings 返回正确格式
- [ ] POST /api/backtest/settings 能保存参数
- [ ] 无效参数被正确拒绝

### 3. 前端功能
- [ ] 参数输入框正常工作
- [ ] 预览计算正确
- [ ] 表单验证有效
- [ ] 下拉菜单和自定义选项正确切换

### 4. 回测功能
- [ ] 不同初始资金产生不同持仓数量
- [ ] 手续费正确应用到成本
- [ ] 滑点正确应用到价格
- [ ] 回测结果包含配置信息

### 5. 极端情况
- [ ] 小初始资金 (10000元)
- [ ] 大交易占比 (90%)
- [ ] 高手续费 (5%)
- [ ] 大滑点 (5%)

## 测试结果

### 单元测试结果
```
测试文件: tests/test_backtest_new_features.py
通过: [数量]
失败: [数量]
覆盖率: [百分比]
```

### 集成测试结果
```
测试文件: test_config_flow.py
通过: [数量]
失败: [数量]
```

## 问题记录

| 问题ID | 描述 | 严重等级 | 状态 |
|--------|------|---------|------|
| [ID]   | [描述] | [等级] | [状态] |

## 建议和改进

[记录任何发现的改进机会]

## 签字
- 测试负责人: [名字]
- 日期: [日期]
```

#### 任务4.4: 执行测试计划

```
测试执行步骤：

1. 单元测试
   cd D:\ai_work\stock_test
   python -m pytest tests/test_backtest_new_features.py -v

2. 集成测试
   - 启动应用: python app_with_cache.py
   - 运行集成测试: python test_config_flow.py

3. 手动测试清单
   - 打开 http://localhost:5000
   - 测试各参数的输入范围
   - 修改参数并运行回测
   - 验证结果中包含配置信息

4. 记录测试结果到 TEST_REPORT.md
```

### 与其他团队的通讯要点

接收来自：
- **config-manager**: 参数验证规则
- **backtest-engine-dev**: 计算公式和结果格式
- **frontend-developer**: 参数输入格式和验证规则

### 文件所有权
- `tests/test_backtest_new_features.py` ✓ (新建)
- `test_config_flow.py` ✓ (新建)
- `TEST_REPORT.md` ✓ (新建)

### 完成检查清单
- [ ] 单元测试文件已创建，所有测试通过
- [ ] 集成测试脚本已创建，所有测试通过
- [ ] 参数范围验证正确
- [ ] 计算公式验证正确
- [ ] 极端情况测试通过
- [ ] 测试报告已生成
- [ ] 所有问题已解决或记录

---

## 执行流程总结

### 阶段1：配置设计 (config-manager)
1. 修改 strategy_config.json 添加4个参数
2. 在 config.py 添加常量和验证函数
3. 在 app_with_cache.py 添加2个API端点
4. **通知其他团队** ← 关键

### 阶段2：并行实现 (backtest-engine-dev + frontend-developer)
- **backtest-engine-dev**: 更新回测逻辑应用配置
- **frontend-developer**: 创建参数输入UI

### 阶段3：集成测试 (qa-tester)
1. 运行单元测试验证逻辑
2. 运行集成测试验证流程
3. 手动测试所有功能
4. 生成测试报告

### 阶段4：反馈和修改
- 根据测试反馈修改代码
- 重新测试直到所有功能正常

---

## 通讯模板

### config-manager → 其他团队
```
标题: 配置参数结构已完成 - 请开始实现

亲爱的团队成员，

配置管理工作已完成。以下是你们需要的信息：

[包含参数结构、API端点、验证规则等]

请基于此设计进行你们的开发工作。

谢谢！
```

### 团队 → qa-tester
```
标题: [模块名] 实现完成 - 等待测试

你好，

[模块名]的实现已完成，包含以下功能：
- [功能1]
- [功能2]
...

请进行测试并报告任何问题。

谢谢！
```

---

## 项目关键路径

| 开发者 | 文件 | 行数 | 优先级 |
|--------|------|------|--------|
| config-manager | strategy_config.json | - | 高 |
| config-manager | config.py | +30 | 高 |
| config-manager | app_with_cache.py | +40 | 高 |
| backtest-engine-dev | backtest_engine.py | +150 | 高 |
| frontend-developer | index_with_cache.html | +400 | 高 |
| qa-tester | test_backtest_new_features.py | 300+ | 中 |
| qa-tester | test_config_flow.py | 100+ | 中 |

---

## 完成检查清单（整体）

- [ ] 配置参数已设计和实现
- [ ] API端点已实现和文档化
- [ ] 回测引擎已更新
- [ ] 前端UI已完成
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 无代码语法错误
- [ ] 功能文档已完成
- [ ] 整个流程验证无误

---

**项目启动时间**: 2026-02-24
**预计完成时间**: [待定]
**项目路径**: D:\ai_work\stock_test
```
