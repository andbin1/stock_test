"""测试参数验证 - 验证所有参数的验证规则"""
import pytest
from config import (
    validate_trading_settings,
    INITIAL_CAPITAL_MIN, INITIAL_CAPITAL_MAX,
    POSITION_RATIO_MIN, POSITION_RATIO_MAX,
    COMMISSION_RATE_MIN, COMMISSION_RATE_MAX,
    SLIPPAGE_MIN, SLIPPAGE_MAX
)


class TestInitialCapitalValidation:
    """初始资金验证"""

    def test_minimum_boundary(self):
        """测试最小值边界"""
        settings = {'initial_capital': INITIAL_CAPITAL_MIN}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最小值 {INITIAL_CAPITAL_MIN} 应被接受，但返回: {msg}"

    def test_maximum_boundary(self):
        """测试最大值边界"""
        settings = {'initial_capital': INITIAL_CAPITAL_MAX}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最大值 {INITIAL_CAPITAL_MAX} 应被接受，但返回: {msg}"

    def test_below_minimum(self):
        """测试低于最小值"""
        settings = {'initial_capital': INITIAL_CAPITAL_MIN - 1}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"低于最小值的 {INITIAL_CAPITAL_MIN - 1} 应被拒绝"
        assert "初始金额" in msg, f"错误消息应包含'初始金额'，但为: {msg}"

    def test_above_maximum(self):
        """测试高于最大值"""
        settings = {'initial_capital': INITIAL_CAPITAL_MAX + 1}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"高于最大值的 {INITIAL_CAPITAL_MAX + 1} 应被拒绝"
        assert "初始金额" in msg

    def test_negative_value(self):
        """测试负数"""
        settings = {'initial_capital': -10000}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "负值应被拒绝"

    def test_decimal_value(self):
        """测试小数值"""
        settings = {'initial_capital': 50000.50}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"小数值应被接受，但返回: {msg}"

    def test_zero_value(self):
        """测试零值"""
        settings = {'initial_capital': 0}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "零值应被拒绝"

    def test_common_values(self):
        """测试常见值"""
        for value in [50000, 100000, 500000, 1000000]:
            settings = {'initial_capital': value}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid, f"常见值 {value} 应被接受"


class TestPositionRatioValidation:
    """交易占比验证"""

    def test_minimum_boundary(self):
        """测试最小值边界"""
        settings = {'position_ratio': POSITION_RATIO_MIN}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最小值 {POSITION_RATIO_MIN} 应被接受，但返回: {msg}"

    def test_maximum_boundary(self):
        """测试最大值边界"""
        settings = {'position_ratio': POSITION_RATIO_MAX}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最大值 {POSITION_RATIO_MAX} 应被接受，但返回: {msg}"

    def test_below_minimum(self):
        """测试低于最小值"""
        settings = {'position_ratio': POSITION_RATIO_MIN - 0.001}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"低于最小值应被拒绝"
        assert "交易占比" in msg

    def test_above_maximum(self):
        """测试高于最大值"""
        settings = {'position_ratio': POSITION_RATIO_MAX + 0.001}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"高于最大值应被拒绝"
        assert "交易占比" in msg

    def test_zero_value_rejected(self):
        """测试零值应被拒绝"""
        settings = {'position_ratio': 0}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "零值应被拒绝"

    def test_one_value_rejected(self):
        """测试1.0应被拒绝"""
        settings = {'position_ratio': 1.0}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "1.0值应被拒绝"

    def test_precision(self):
        """测试小数点精度"""
        # 测试3位小数
        settings = {'position_ratio': 0.333}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"0.333 应被接受"

        # 测试4位小数
        settings = {'position_ratio': 0.3333}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"0.3333 应被接受"

    def test_common_values(self):
        """测试常见预设值"""
        for value in [0.1, 0.2, 0.333, 0.5]:  # 1/10, 1/5, 1/3, 1/2
            settings = {'position_ratio': value}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid, f"常见值 {value} 应被接受"


class TestCommissionRateValidation:
    """手续费验证"""

    def test_minimum_boundary(self):
        """测试最小值边界"""
        settings = {'commission_rate': COMMISSION_RATE_MIN}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最小值 {COMMISSION_RATE_MIN} 应被接受"

    def test_maximum_boundary(self):
        """测试最大值边界"""
        settings = {'commission_rate': COMMISSION_RATE_MAX}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最大值 {COMMISSION_RATE_MAX} 应被接受"

    def test_below_minimum(self):
        """测试负数"""
        settings = {'commission_rate': -0.001}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"负数应被拒绝"
        assert "手续费" in msg

    def test_above_maximum(self):
        """测试超过5%"""
        settings = {'commission_rate': 0.051}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"超过5%应被拒绝"
        assert "手续费" in msg

    def test_zero_commission(self):
        """测试零手续费"""
        settings = {'commission_rate': 0}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "零手续费应被接受"

    def test_common_rates(self):
        """测试常见手续费"""
        # 万1 = 0.0001, 万2.5 = 0.00025, 万5 = 0.0005
        for value in [0.0001, 0.00025, 0.0005, 0.001]:
            settings = {'commission_rate': value}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid, f"常见费率 {value} 应被接受"

    def test_extreme_high_value(self):
        """测试极高手续费"""
        settings = {'commission_rate': 1.0}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "100%手续费应被拒绝"


class TestSlippageValidation:
    """滑点验证"""

    def test_minimum_boundary(self):
        """测试最小值边界"""
        settings = {'slippage': SLIPPAGE_MIN}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最小值 {SLIPPAGE_MIN} 应被接受"

    def test_maximum_boundary(self):
        """测试最大值边界"""
        settings = {'slippage': SLIPPAGE_MAX}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"最大值 {SLIPPAGE_MAX} 应被接受"

    def test_below_minimum(self):
        """测试负数"""
        settings = {'slippage': -0.001}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"负数应被拒绝"
        assert "滑点" in msg

    def test_above_maximum(self):
        """测试超过5%"""
        settings = {'slippage': 0.051}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"超过5%应被拒绝"
        assert "滑点" in msg

    def test_zero_slippage(self):
        """测试零滑点"""
        settings = {'slippage': 0}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "零滑点应被接受"

    def test_common_slippage(self):
        """测试常见滑点"""
        for value in [0.001, 0.002, 0.005, 0.01]:  # 0.1%, 0.2%, 0.5%, 1%
            settings = {'slippage': value}
            is_valid, msg = validate_trading_settings(settings)
            assert is_valid, f"常见滑点 {value} 应被接受"


class TestCombinedValidation:
    """组合参数验证"""

    def test_all_valid_parameters(self):
        """测试所有参数都有效"""
        settings = {
            'initial_capital': 100000,
            'position_ratio': 0.2,
            'commission_rate': 0.001,
            'slippage': 0.005
        }
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, f"所有参数有效时应通过: {msg}"

    def test_one_invalid_parameter(self):
        """测试一个参数无效"""
        settings = {
            'initial_capital': 100000,
            'position_ratio': 1.5,  # 无效
            'commission_rate': 0.001,
            'slippage': 0.005
        }
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "存在无效参数时应拒绝"
        assert "交易占比" in msg

    def test_all_minimum_values(self):
        """测试所有最小值"""
        settings = {
            'initial_capital': INITIAL_CAPITAL_MIN,
            'position_ratio': POSITION_RATIO_MIN,
            'commission_rate': COMMISSION_RATE_MIN,
            'slippage': SLIPPAGE_MIN
        }
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "所有最小值应被接受"

    def test_all_maximum_values(self):
        """测试所有最大值"""
        settings = {
            'initial_capital': INITIAL_CAPITAL_MAX,
            'position_ratio': POSITION_RATIO_MAX,
            'commission_rate': COMMISSION_RATE_MAX,
            'slippage': SLIPPAGE_MAX
        }
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "所有最大值应被接受"

    def test_empty_settings(self):
        """测试空设置"""
        settings = {}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "空设置应被接受（部分参数验证）"

    def test_single_parameter_validation(self):
        """测试单个参数验证（其他参数不受影响）"""
        # 验证initial_capital，不验证其他参数
        settings = {'initial_capital': 100000}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "单个参数验证应通过"

        # 验证position_ratio，不验证其他参数
        settings = {'position_ratio': 0.2}
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "单个参数验证应通过"


class TestEdgeCases:
    """边界情况测试"""

    def test_very_small_decimal(self):
        """测试极小的小数"""
        settings = {'position_ratio': 0.00001}
        is_valid, msg = validate_trading_settings(settings)
        # 应低于最小值
        assert not is_valid, "极小值应被拒绝"

    def test_very_large_decimal(self):
        """测试极接近1的小数"""
        settings = {'position_ratio': 0.99999}
        is_valid, msg = validate_trading_settings(settings)
        # 应高于最大值
        assert not is_valid, "极接近1的值应被拒绝"

    def test_integer_as_float(self):
        """测试整数作为浮点数"""
        settings = {'position_ratio': float(1)}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, "1.0应被拒绝"

    def test_scientific_notation(self):
        """测试科学计数法"""
        settings = {'initial_capital': 1e5}  # 100000
        is_valid, msg = validate_trading_settings(settings)
        assert is_valid, "科学计数法应被转换并接受"

    def test_boundary_plus_epsilon(self):
        """测试边界 + 极小偏差"""
        epsilon = 0.00000001

        # initial_capital
        settings = {'initial_capital': INITIAL_CAPITAL_MAX + epsilon}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"超过最大值 {epsilon} 应被拒绝"

    def test_boundary_minus_epsilon(self):
        """测试边界 - 极小偏差"""
        epsilon = 0.00000001

        # initial_capital
        settings = {'initial_capital': INITIAL_CAPITAL_MIN - epsilon}
        is_valid, msg = validate_trading_settings(settings)
        assert not is_valid, f"低于最小值 {epsilon} 应被拒绝"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
