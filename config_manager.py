"""参数配置管理模块 - 支持动态修改策略参数"""
import json
from pathlib import Path
from config import STRATEGY_PARAMS, START_DATE, END_DATE, STRATEGY_MAP, DEFAULT_STRATEGY

CONFIG_FILE = Path("./strategy_config.json")

class ConfigManager:
    """策略参数配置管理"""

    def __init__(self):
        self.config_file = CONFIG_FILE
        self.default_params = STRATEGY_PARAMS.copy()
        self.current_strategy = DEFAULT_STRATEGY
        self.load_or_init()

    def load_or_init(self):
        """加载或初始化配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # 兼容新旧格式
                    if isinstance(config_data, dict) and 'current_strategy' in config_data:
                        self.current_strategy = config_data.get('current_strategy', DEFAULT_STRATEGY)
                        self.current_params = config_data.get('params', self.default_params.copy())
                    else:
                        # 旧格式，直接是参数字典
                        self.current_params = config_data
            except Exception as e:
                print(f"读取配置文件失败: {e}，使用默认参数")
                self.current_params = self.default_params.copy()
                self.save()
        else:
            self.current_params = self.default_params.copy()
            self.save()

    def save(self):
        """保存配置到文件"""
        try:
            config_data = {
                'current_strategy': self.current_strategy,
                'params': self.current_params
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_params(self):
        """获取当前参数"""
        return self.current_params.copy()

    def update_params(self, new_params: dict):
        """更新参数

        Args:
            new_params: 新参数字典，只需包含要修改的参数

        Returns:
            (成功: bool, 消息: str)
        """
        # 验证参数
        validation_result = self.validate_params(new_params)
        if not validation_result['valid']:
            return False, validation_result['message']

        # 更新参数
        self.current_params.update(new_params)

        # 保存到文件
        if self.save():
            return True, "✓ 参数已更新"
        else:
            return False, "✗ 保存参数失败"

    def validate_params(self, params: dict) -> dict:
        """验证参数有效性"""
        try:
            # 检查 ma_period
            if 'ma_period' in params:
                ma = params['ma_period']
                if not isinstance(ma, int) or ma < 5 or ma > 250:
                    return {
                        'valid': False,
                        'message': 'MA周期必须是 5-250 之间的整数'
                    }

            # 检查 volume_multiplier
            if 'volume_multiplier' in params:
                vm = params['volume_multiplier']
                if not isinstance(vm, (int, float)) or vm < 0.5 or vm > 10:
                    return {
                        'valid': False,
                        'message': '量能倍数必须是 0.5-10 之间的数字'
                    }

            # 检查 retest_period
            if 'retest_period' in params:
                rp = params['retest_period']
                if not isinstance(rp, int) or rp < 3 or rp > 20:
                    return {
                        'valid': False,
                        'message': '回踩周期必须是 3-20 之间的整数'
                    }

            # 检查 hold_days
            if 'hold_days' in params:
                hd = params['hold_days']
                if not isinstance(hd, int) or hd < 1 or hd > 10:
                    return {
                        'valid': False,
                        'message': '持有天数必须是 1-10 之间的整数'
                    }

            # 检查 turnover_min（最小成交金额，单位亿）
            if 'turnover_min' in params:
                tm = params['turnover_min']
                if not isinstance(tm, (int, float)) or tm < 0.01 or tm > 1000:
                    return {
                        'valid': False,
                        'message': '最小成交金额必须是 0.01-1000 亿之间的数字'
                    }

            # 检查 turnover_max（最大成交金额，单位亿）
            if 'turnover_max' in params:
                tm = params['turnover_max']
                if not isinstance(tm, (int, float)) or tm < 0.01 or tm > 1000:
                    return {
                        'valid': False,
                        'message': '最大成交金额必须是 0.01-1000 亿之间的数字'
                    }

            # 检查 turnover_min 和 turnover_max 的关系
            if 'turnover_min' in params and 'turnover_max' in params:
                if params['turnover_min'] > params['turnover_max']:
                    return {
                        'valid': False,
                        'message': '最小成交金额不能大于最大成交金额'
                    }

            return {'valid': True, 'message': '参数验证通过'}

        except Exception as e:
            return {
                'valid': False,
                'message': f'参数验证失败: {e}'
            }

    def reset_to_default(self):
        """重置为默认参数"""
        self.current_params = self.default_params.copy()
        if self.save():
            return True, "✓ 已重置为默认参数"
        else:
            return False, "✗ 重置失败"

    def get_param_ranges(self):
        """获取参数范围（用于前端验证）"""
        return {
            'ma_period': {'min': 5, 'max': 250, 'step': 1, 'type': 'integer'},
            'volume_multiplier': {'min': 0.5, 'max': 10, 'step': 0.1, 'type': 'number'},
            'retest_period': {'min': 3, 'max': 20, 'step': 1, 'type': 'integer'},
            'hold_days': {'min': 1, 'max': 10, 'step': 1, 'type': 'integer'},
            'turnover_min': {'min': 0.01, 'max': 1000, 'step': 1, 'type': 'number'},
            'turnover_max': {'min': 0.01, 'max': 1000, 'step': 1, 'type': 'number'},
        }

    def get_param_descriptions(self):
        """获取参数描述"""
        return {
            'ma_period': '30日均线周期（天），用于判断上升趋势',
            'volume_multiplier': '量能倍数，最近3日总量能 vs 20日均量能 * 倍数',
            'retest_period': '5日线周期（天），用于检测价格回踩',
            'hold_days': '持有天数（交易日），买入后N天卖出',
            'turnover_min': '上一交易日成交金额最小值（亿元）',
            'turnover_max': '上一交易日成交金额最大值（亿元）',
        }

    def export_preset(self, name: str, params: dict) -> bool:
        """保存参数预设"""
        presets_file = Path("./strategy_presets.json")

        try:
            if presets_file.exists():
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
            else:
                presets = {}

            presets[name] = params

            with open(presets_file, 'w', encoding='utf-8') as f:
                json.dump(presets, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存预设失败: {e}")
            return False

    def load_preset(self, name: str) -> tuple:
        """加载参数预设

        Returns:
            (成功: bool, 参数或消息)
        """
        presets_file = Path("./strategy_presets.json")

        try:
            if not presets_file.exists():
                return False, "预设文件不存在"

            with open(presets_file, 'r', encoding='utf-8') as f:
                presets = json.load(f)

            if name not in presets:
                return False, f"预设 '{name}' 不存在"

            return True, presets[name]
        except Exception as e:
            return False, f"加载预设失败: {e}"

    def get_all_presets(self) -> dict:
        """获取所有预设"""
        presets_file = Path("./strategy_presets.json")

        try:
            if presets_file.exists():
                with open(presets_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"读取预设失败: {e}")
            return {}

    def get_strategy_list(self) -> list:
        """获取所有可用策略列表"""
        return [
            {
                'key': key,
                'name': value['name'],
                'description': value['description'],
            }
            for key, value in STRATEGY_MAP.items()
        ]

    def get_current_strategy(self) -> str:
        """获取当前选择的策略"""
        return self.current_strategy

    def set_current_strategy(self, strategy_key: str) -> tuple:
        """设置当前策略"""
        if strategy_key not in STRATEGY_MAP:
            return False, f"策略 {strategy_key} 不存在"

        self.current_strategy = strategy_key
        self.current_params = STRATEGY_MAP[strategy_key]['params'].copy()
        self.default_params = self.current_params.copy()
        self.save()

        return True, f"已切换到策略: {STRATEGY_MAP[strategy_key]['name']}"

    def get_strategy_params(self, strategy_key: str = None) -> dict:
        """获取指定策略的参数"""
        if strategy_key is None:
            strategy_key = self.current_strategy

        if strategy_key not in STRATEGY_MAP:
            return {}

        return STRATEGY_MAP[strategy_key]['params'].copy()

    def get_config_info(self) -> dict:
        """获取完整配置信息（用于前端）"""
        return {
            'current_strategy': self.current_strategy,
            'strategies': self.get_strategy_list(),
            'current_params': self.get_params(),
            'default_params': self.default_params,
            'ranges': self.get_param_ranges(),
            'descriptions': self.get_param_descriptions(),
            'presets': self.get_all_presets(),
            'config_file': str(self.config_file)
        }


# 命令行工具
if __name__ == "__main__":
    import sys

    manager = ConfigManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            print("\n" + "="*60)
            print("  策略参数配置")
            print("="*60)
            print()
            info = manager.get_config_info()
            print("当前参数:")
            for key, value in info['current_params'].items():
                default = info['default_params'][key]
                print(f"  {key}: {value} (默认: {default})")
            print()

        elif command == "reset":
            success, msg = manager.reset_to_default()
            print(msg)

        elif command == "set":
            if len(sys.argv) > 3:
                param_name = sys.argv[2]
                param_value = sys.argv[3]

                # 尝试转换为适当的类型
                try:
                    if param_name in ['ma_period', 'retest_period', 'hold_days']:
                        param_value = int(param_value)
                    else:
                        param_value = float(param_value)
                except ValueError:
                    print(f"✗ 参数值无效: {param_value}")
                    sys.exit(1)

                success, msg = manager.update_params({param_name: param_value})
                print(msg)
            else:
                print("用法: python config_manager.py set <参数名> <参数值>")

        elif command == "save-preset":
            if len(sys.argv) > 2:
                preset_name = sys.argv[2]
                if manager.export_preset(preset_name, manager.get_params()):
                    print(f"✓ 预设 '{preset_name}' 已保存")
                else:
                    print(f"✗ 保存预设失败")
            else:
                print("用法: python config_manager.py save-preset <预设名>")

        elif command == "load-preset":
            if len(sys.argv) > 2:
                preset_name = sys.argv[2]
                success, result = manager.load_preset(preset_name)
                if success:
                    manager.update_params(result)
                    print(f"✓ 已加载预设 '{preset_name}'")
                else:
                    print(f"✗ {result}")
            else:
                print("用法: python config_manager.py load-preset <预设名>")

        elif command == "list-presets":
            presets = manager.get_all_presets()
            if presets:
                print("\n已保存的预设:")
                for name, params in presets.items():
                    print(f"  {name}: {params}")
            else:
                print("暂无预设")

    else:
        print("""
参数配置管理工具

用法:
  python config_manager.py status              查看当前参数
  python config_manager.py set <名> <值>      设置参数
  python config_manager.py reset               重置为默认
  python config_manager.py save-preset <名>   保存预设
  python config_manager.py load-preset <名>   加载预设
  python config_manager.py list-presets       列出所有预设

示例:
  python config_manager.py set ma_period 20
  python config_manager.py set volume_multiplier 2.5
  python config_manager.py save-preset 激进
  python config_manager.py load-preset 激进
        """)
