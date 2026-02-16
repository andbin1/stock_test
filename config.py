# 配置文件
START_DATE = "20240101"
END_DATE = "20250213"

# 指数配置 - 按板块分类
INDICES = {
    "沪深A股": "000001",      # 上证指数
    "创业板": "399006",        # 创业板指数
    "科创板": "000688",        # 科创板代表
    "深成指": "399001",        # 深圳成分指数
    "中证500": "000905",       # 中证500
}

# 板块对应的指数代码（用于获取成分股）
SECTORS = {
    "沪深A股": {
        "code": "000001",
        "name": "上证指数",
        "description": "沪深A股主板市场"
    },
    "创业板": {
        "code": "399006",
        "name": "创业板指数",
        "description": "深交所创业板"
    },
    "科创板": {
        "code": "000688",
        "name": "科创板代表",
        "description": "上交所科创板"
    },
    "深成指": {
        "code": "399001",
        "name": "深圳成分指数",
        "description": "深交所成分指数"
    },
    "中证500": {
        "code": "000905",
        "name": "中证500",
        "description": "中证500指数"
    },
}

# 获取指数成分股数量
MAX_STOCKS = 20  # 先测试20只，快速验证系统

# 策略参数 - 量能突破回踩策略（原有）
STRATEGY_PARAMS = {
    "ma_period": 30,           # 30日均线周期
    "recent_days": 5,          # 参考值（未直接使用）
    "retest_period": 5,        # 5日线周期
    "hold_days": 3,            # 持有3个交易日
    "volume_multiplier": 3.0,  # 量能倍数（最近3日总量能 > 20日均量能 × 倍数）
    "turnover_min": 0.01,      # 最小成交金额（亿元，0.01=1000万）
    "turnover_max": 1000.0,    # 最大成交金额（亿元，1000=100亿）
}

# 策略1：稳健型趋势跟踪
STEADY_TREND_PARAMS = {
    # 均线参数
    "ma_short": 30,
    "ma_long": 60,
    "ma_filter": 120,

    # 量能参数
    "volume_ma": 20,
    "volume_multiplier": 1.5,

    # MACD参数
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,

    # 止损止盈
    "stop_loss": 0.08,
    "take_profit": 0.15,
    "trailing_stop": 0.05,

    # 仓位管理
    "position_size": 0.20,
}

# 策略2：激进型突破动量
AGGRESSIVE_MOMENTUM_PARAMS = {
    # 突破参数
    "breakout_period": 20,
    "breakout_threshold": 0.03,

    # RSI参数
    "rsi_period": 6,
    "rsi_threshold": 50,

    # 量能参数
    "volume_multiplier": 2.5,

    # KDJ参数
    "kdj_n": 5,
    "kdj_m1": 3,
    "kdj_m2": 3,

    # ATR参数
    "atr_period": 14,
    "atr_stop_mult": 2.0,

    # 持仓控制
    "max_hold_days": 5,
    "trailing_stop": 0.03,

    # 仓位管理
    "position_size": 0.15,
}

# 策略3：平衡型多因子
BALANCED_MULTI_FACTOR_PARAMS = {
    # 布林带参数
    "boll_period": 20,
    "boll_std": 2.0,

    # RSI参数
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,

    # MACD参数
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,

    # 止损止盈
    "stop_loss": 0.10,
    "take_profit_1": 0.05,
    "take_profit_2": 0.10,
    "take_profit_final": 0.15,

    # 因子权重
    "factor_weight_boll": 0.20,
    "factor_weight_rsi": 0.25,
    "factor_weight_macd": 0.20,
    "factor_weight_volume": 0.15,
    "factor_weight_price": 0.20,

    # 仓位管理
    "position_size": 0.20,
    "min_factor_score": 0.6,
}

# 策略映射
STRATEGY_MAP = {
    "volume_breakout": {
        "name": "量能突破回踩策略",
        "class_name": "VolumeBreakoutStrategy",
        "params": STRATEGY_PARAMS,
        "description": "基于30日均线、量能放大和5日线回踩的经典策略",
    },
    "steady_trend": {
        "name": "稳健型趋势跟踪策略",
        "class_name": "SteadyTrendStrategy",
        "params": STEADY_TREND_PARAMS,
        "description": "适合主板蓝筹股，低频交易，严格风控",
    },
    "aggressive_momentum": {
        "name": "激进型突破动量策略",
        "class_name": "AggressiveMomentumStrategy",
        "params": AGGRESSIVE_MOMENTUM_PARAMS,
        "description": "适合创业板科创板，高频交易，快进快出",
    },
    "balanced_multi_factor": {
        "name": "平衡型多因子策略",
        "class_name": "BalancedMultiFactorStrategy",
        "params": BALANCED_MULTI_FACTOR_PARAMS,
        "description": "适合中证500，多因子评分，分批建仓",
    },
}

# 新增策略（来自strategy_new.py）
# 导入新策略配置
try:
    from config_new_strategies import (
        DOUBLE_MA_PARAMS,
        DOUBLE_MA_AGGRESSIVE_PARAMS,
        DOUBLE_MA_STEADY_PARAMS,
        GRID_TRADING_PARAMS,
        GRID_TRADING_DENSE_PARAMS,
        GRID_TRADING_WIDE_PARAMS,
        TURTLE_TRADING_PARAMS,
        TURTLE_TRADING_AGGRESSIVE_PARAMS,
        TURTLE_TRADING_CONSERVATIVE_PARAMS,
    )

    # 将新策略添加到策略映射
    STRATEGY_MAP["double_ma_cross"] = {
        "name": "双均线交叉策略",
        "class_name": "DoubleMACrossStrategy",
        "params": DOUBLE_MA_PARAMS,
        "description": "经典趋势跟踪策略，胜率65-70%，适合趋势市场",
    }

    STRATEGY_MAP["double_ma_aggressive"] = {
        "name": "双均线交叉策略（激进）",
        "class_name": "DoubleMACrossStrategy",
        "params": DOUBLE_MA_AGGRESSIVE_PARAMS,
        "description": "短周期双均线，交易频率高，适合短线操作",
    }

    STRATEGY_MAP["double_ma_steady"] = {
        "name": "双均线交叉策略（稳健）",
        "class_name": "DoubleMACrossStrategy",
        "params": DOUBLE_MA_STEADY_PARAMS,
        "description": "长周期双均线，交易频率低，适合长线持有",
    }

    STRATEGY_MAP["grid_trading"] = {
        "name": "网格交易策略",
        "class_name": "GridTradingStrategy",
        "params": GRID_TRADING_PARAMS,
        "description": "震荡市首选，胜率70-75%，适合高流动性股票",
    }

    STRATEGY_MAP["grid_trading_dense"] = {
        "name": "网格交易策略（密集）",
        "class_name": "GridTradingStrategy",
        "params": GRID_TRADING_DENSE_PARAMS,
        "description": "网格数量多，利润目标低，交易频繁",
    }

    STRATEGY_MAP["grid_trading_wide"] = {
        "name": "网格交易策略（宽松）",
        "class_name": "GridTradingStrategy",
        "params": GRID_TRADING_WIDE_PARAMS,
        "description": "网格数量少，利润目标高，适合大波动股票",
    }

    STRATEGY_MAP["turtle_trading"] = {
        "name": "海龟交易法则",
        "class_name": "TurtleTradingStrategy",
        "params": TURTLE_TRADING_PARAMS,
        "description": "完整交易系统，盈亏比3:1，适合趋势行情",
    }

    STRATEGY_MAP["turtle_aggressive"] = {
        "name": "海龟交易法则（激进）",
        "class_name": "TurtleTradingStrategy",
        "params": TURTLE_TRADING_AGGRESSIVE_PARAMS,
        "description": "短周期突破，止损宽松，适合激进投资者",
    }

    STRATEGY_MAP["turtle_conservative"] = {
        "name": "海龟交易法则（保守）",
        "class_name": "TurtleTradingStrategy",
        "params": TURTLE_TRADING_CONSERVATIVE_PARAMS,
        "description": "长周期突破，止损严格，适合稳健投资者",
    }

except ImportError:
    # 如果新策略配置文件不存在，忽略
    pass

# 默认策略
DEFAULT_STRATEGY = "volume_breakout"

# 回测参数
INITIAL_CAPITAL = 100000   # 初始资金10万元
COMMISSION_RATE = 0.00025  # 手续费率 万2.5 (买卖双向)
STAMP_TAX = 0.001          # 印花税 千1 (仅卖出)
SLIPPAGE = 0.001           # 滑点 0.1%
TRADING_FEE_MIN = 5        # 最低手续费 5元（单边）
