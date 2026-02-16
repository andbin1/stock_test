"""
新策略配置文件
包含双均线、网格交易、海龟交易三个策略的参数配置
"""

# ====================================================================
# 策略1：双均线交叉策略（Moving Average Crossover）
# ====================================================================
# 适用场景：趋势明显的市场，主板蓝筹股
# 预期收益：年化12-18%，胜率65-70%
# 交易频率：中频（月均2-5次）
# ====================================================================

DOUBLE_MA_PARAMS = {
    # 均线参数
    "ma_short": 5,              # 短期均线周期（日）
    "ma_long": 20,              # 长期均线周期（日）
    "ma_filter": 60,            # 趋势过滤均线（日），价格需在其上方

    # 量能过滤
    "volume_filter": True,      # 是否启用量能过滤
    "volume_ratio": 1.5,        # 量能倍数阈值（当日成交量 > 20日均量 × 倍数）

    # 止损止盈
    "use_stop_loss": True,      # 是否使用止损
    "stop_loss": 0.08,          # 止损幅度（8%）
    "use_take_profit": True,    # 是否使用止盈
    "take_profit": 0.15,        # 固定止盈幅度（15%）
    "trailing_stop": 0.05,      # 移动止盈幅度（5%，从最高点回落触发）
}

# 双均线策略变体1：激进型（适合成长股）
DOUBLE_MA_AGGRESSIVE_PARAMS = {
    "ma_short": 3,              # 更短的均线，反应更快
    "ma_long": 10,
    "ma_filter": 30,
    "volume_filter": True,
    "volume_ratio": 2.0,        # 更高的量能要求
    "use_stop_loss": True,
    "stop_loss": 0.05,          # 更紧的止损
    "use_take_profit": True,
    "take_profit": 0.10,        # 更快止盈
    "trailing_stop": 0.03,
}

# 双均线策略变体2：稳健型（适合大盘股）
DOUBLE_MA_STEADY_PARAMS = {
    "ma_short": 10,             # 更长的均线，减少假信号
    "ma_long": 30,
    "ma_filter": 120,
    "volume_filter": True,
    "volume_ratio": 1.3,
    "use_stop_loss": True,
    "stop_loss": 0.10,          # 更宽的止损
    "use_take_profit": True,
    "take_profit": 0.20,        # 更高的止盈目标
    "trailing_stop": 0.08,
}


# ====================================================================
# 策略2：网格交易策略（Grid Trading）
# ====================================================================
# 适用场景：震荡市场，高流动性股票
# 预期收益：年化15-25%（震荡市），胜率70-75%
# 交易频率：高频（月均10-20次）
# ====================================================================

GRID_TRADING_PARAMS = {
    # 网格参数
    "grid_levels": 5,           # 网格层数（5层）
    "price_range": 0.20,        # 价格波动范围（20%）
    "grid_profit": 0.03,        # 每格利润目标（3%）

    # 仓位管理
    "base_position": 0.20,      # 基础仓位大小（20%）
    "max_positions": 3,         # 最大持仓网格数（3个）

    # ATR动态网格（可选）
    "use_atr": False,           # 是否使用ATR动态网格
    "atr_period": 14,           # ATR周期
    "atr_multiplier": 2.0,      # ATR倍数

    # 网格重置
    "rebalance_days": 20,       # 网格重置周期（天）
}

# 网格策略变体1：密集网格（适合低波动标的）
GRID_TRADING_DENSE_PARAMS = {
    "grid_levels": 10,          # 更多网格层
    "price_range": 0.15,        # 更窄的价格范围
    "grid_profit": 0.02,        # 更小的利润目标
    "base_position": 0.15,
    "max_positions": 5,         # 更多持仓网格
    "use_atr": False,
    "atr_period": 14,
    "atr_multiplier": 1.5,
    "rebalance_days": 15,
}

# 网格策略变体2：宽松网格（适合高波动标的）
GRID_TRADING_WIDE_PARAMS = {
    "grid_levels": 3,           # 更少网格层
    "price_range": 0.30,        # 更宽的价格范围
    "grid_profit": 0.05,        # 更大的利润目标
    "base_position": 0.25,
    "max_positions": 2,
    "use_atr": True,            # 使用ATR适应波动
    "atr_period": 14,
    "atr_multiplier": 2.5,
    "rebalance_days": 30,
}


# ====================================================================
# 策略3：海龟交易法则（Turtle Trading）
# ====================================================================
# 适用场景：趋势明显的市场，大盘股和指数
# 预期收益：年化15-30%，胜率40-50%，盈亏比3:1
# 交易频率：低频（月均1-3次）
# ====================================================================

TURTLE_TRADING_PARAMS = {
    # 突破参数
    "entry_period": 20,         # 入场突破周期（20日最高价）
    "exit_period": 10,          # 出场突破周期（10日最低价）

    # ATR参数
    "atr_period": 20,           # ATR周期
    "atr_stop_mult": 2.0,       # ATR止损倍数（2倍ATR）
    "pyramid_atr": 0.5,         # 加仓间距（0.5倍ATR）

    # 风险管理
    "risk_per_trade": 0.02,     # 单笔交易风险（2%）
    "max_units": 4,             # 最大持仓单位数（4个）

    # 趋势过滤
    "use_filter": True,         # 是否使用趋势过滤
    "filter_period": 60,        # 趋势过滤周期（60日均线）
}

# 海龟策略变体1：激进型（适合牛市）
TURTLE_TRADING_AGGRESSIVE_PARAMS = {
    "entry_period": 10,         # 更短的突破周期，更早入场
    "exit_period": 5,
    "atr_period": 14,
    "atr_stop_mult": 1.5,       # 更紧的止损
    "pyramid_atr": 0.3,         # 更频繁的加仓
    "risk_per_trade": 0.03,     # 更高的风险
    "max_units": 5,
    "use_filter": False,        # 不使用过滤
    "filter_period": 60,
}

# 海龟策略变体2：保守型（适合熊市）
TURTLE_TRADING_CONSERVATIVE_PARAMS = {
    "entry_period": 40,         # 更长的突破周期，确认趋势
    "exit_period": 20,
    "atr_period": 30,
    "atr_stop_mult": 3.0,       # 更宽的止损
    "pyramid_atr": 1.0,         # 更谨慎的加仓
    "risk_per_trade": 0.01,     # 更低的风险
    "max_units": 2,
    "use_filter": True,
    "filter_period": 120,
}


# ====================================================================
# 策略映射表（便于回测系统调用）
# ====================================================================

NEW_STRATEGY_MAP = {
    # 双均线策略系列
    "double_ma_cross": {
        "name": "双均线交叉策略",
        "class_name": "DoubleMACrossStrategy",
        "params": DOUBLE_MA_PARAMS,
        "description": "经典趋势跟踪策略，适合主板蓝筹股",
        "适用市场": "趋势市场",
        "风险等级": "中",
        "预期收益": "12-18%",
        "胜率": "65-70%",
    },
    "double_ma_aggressive": {
        "name": "双均线交叉策略（激进）",
        "class_name": "DoubleMACrossStrategy",
        "params": DOUBLE_MA_AGGRESSIVE_PARAMS,
        "description": "激进型双均线，适合创业板成长股",
        "适用市场": "牛市",
        "风险等级": "高",
        "预期收益": "18-30%",
        "胜率": "60-65%",
    },
    "double_ma_steady": {
        "name": "双均线交叉策略（稳健）",
        "class_name": "DoubleMACrossStrategy",
        "params": DOUBLE_MA_STEADY_PARAMS,
        "description": "稳健型双均线，适合沪深300大盘股",
        "适用市场": "震荡市场",
        "风险等级": "低",
        "预期收益": "10-15%",
        "胜率": "70-75%",
    },

    # 网格交易策略系列
    "grid_trading": {
        "name": "网格交易策略",
        "class_name": "GridTradingStrategy",
        "params": GRID_TRADING_PARAMS,
        "description": "震荡市高手，适合高流动性股票",
        "适用市场": "震荡市场",
        "风险等级": "中",
        "预期收益": "15-25%",
        "胜率": "70-75%",
    },
    "grid_trading_dense": {
        "name": "网格交易策略（密集）",
        "class_name": "GridTradingStrategy",
        "params": GRID_TRADING_DENSE_PARAMS,
        "description": "密集网格，适合低波动标的",
        "适用市场": "窄幅震荡",
        "风险等级": "低",
        "预期收益": "10-20%",
        "胜率": "75-80%",
    },
    "grid_trading_wide": {
        "name": "网格交易策略（宽松）",
        "class_name": "GridTradingStrategy",
        "params": GRID_TRADING_WIDE_PARAMS,
        "description": "宽松网格，适合高波动标的",
        "适用市场": "宽幅震荡",
        "风险等级": "高",
        "预期收益": "20-35%",
        "胜率": "60-70%",
    },

    # 海龟交易法则系列
    "turtle_trading": {
        "name": "海龟交易法则",
        "class_name": "TurtleTradingStrategy",
        "params": TURTLE_TRADING_PARAMS,
        "description": "经典趋势跟踪系统，适合大盘股和指数",
        "适用市场": "趋势市场",
        "风险等级": "中",
        "预期收益": "15-30%",
        "胜率": "40-50%",
    },
    "turtle_trading_aggressive": {
        "name": "海龟交易法则（激进）",
        "class_name": "TurtleTradingStrategy",
        "params": TURTLE_TRADING_AGGRESSIVE_PARAMS,
        "description": "激进型海龟，适合牛市",
        "适用市场": "牛市",
        "风险等级": "高",
        "预期收益": "25-45%",
        "胜率": "35-45%",
    },
    "turtle_trading_conservative": {
        "name": "海龟交易法则（保守）",
        "class_name": "TurtleTradingStrategy",
        "params": TURTLE_TRADING_CONSERVATIVE_PARAMS,
        "description": "保守型海龟，适合熊市防守",
        "适用市场": "熊市",
        "风险等级": "低",
        "预期收益": "8-15%",
        "胜率": "50-60%",
    },
}


# ====================================================================
# 策略选择建议
# ====================================================================

STRATEGY_SELECTION_GUIDE = {
    "牛市": ["double_ma_aggressive", "turtle_trading_aggressive", "double_ma_cross"],
    "熊市": ["turtle_trading_conservative", "grid_trading", "double_ma_steady"],
    "震荡市": ["grid_trading", "grid_trading_dense", "double_ma_steady"],
    "高波动": ["grid_trading_wide", "turtle_trading_aggressive", "double_ma_aggressive"],
    "低波动": ["grid_trading_dense", "double_ma_steady", "turtle_trading_conservative"],
    "主板蓝筹": ["double_ma_cross", "turtle_trading", "double_ma_steady"],
    "创业板": ["double_ma_aggressive", "turtle_trading_aggressive", "grid_trading_wide"],
    "ETF指数": ["turtle_trading", "double_ma_cross", "grid_trading"],
}


# ====================================================================
# 使用示例
# ====================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("新策略配置预览")
    print("=" * 80)

    print("\n1. 双均线交叉策略参数：")
    for key, value in DOUBLE_MA_PARAMS.items():
        print(f"   {key}: {value}")

    print("\n2. 网格交易策略参数：")
    for key, value in GRID_TRADING_PARAMS.items():
        print(f"   {key}: {value}")

    print("\n3. 海龟交易法则参数：")
    for key, value in TURTLE_TRADING_PARAMS.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 80)
    print("策略映射表：")
    print("=" * 80)
    for strategy_id, strategy_info in NEW_STRATEGY_MAP.items():
        print(f"\n策略ID: {strategy_id}")
        print(f"  名称: {strategy_info['name']}")
        print(f"  描述: {strategy_info['description']}")
        print(f"  适用市场: {strategy_info['适用市场']}")
        print(f"  风险等级: {strategy_info['风险等级']}")
        print(f"  预期收益: {strategy_info['预期收益']}")
        print(f"  胜率: {strategy_info['胜率']}")

    print("\n" + "=" * 80)
    print("策略选择建议：")
    print("=" * 80)
    for market_type, strategies in STRATEGY_SELECTION_GUIDE.items():
        print(f"\n{market_type}环境推荐策略：")
        for i, strategy_id in enumerate(strategies, 1):
            strategy_name = NEW_STRATEGY_MAP[strategy_id]['name']
            print(f"  {i}. {strategy_name} ({strategy_id})")
