"""Web应用 - 集成本地缓存和手动更新功能"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
from io import BytesIO
from datetime import datetime
import threading

from config import START_DATE, END_DATE, STRATEGY_PARAMS, MAX_STOCKS, SECTORS, STRATEGY_MAP, DEFAULT_STRATEGY
from demo_test_debug import generate_better_mock_data
from strategy import VolumeBreakoutStrategy, SteadyTrendStrategy, AggressiveMomentumStrategy, BalancedMultiFactorStrategy

# 导入新策略
try:
    from strategy_new import DoubleMACrossStrategy, GridTradingStrategy, TurtleTradingStrategy
    NEW_STRATEGIES_AVAILABLE = True
except ImportError:
    NEW_STRATEGIES_AVAILABLE = False
    DoubleMACrossStrategy = None
    GridTradingStrategy = None
    TurtleTradingStrategy = None
from export_to_excel import export_detailed_trades_to_excel, export_batch_results_to_excel
from backtest_engine_enhanced import EnhancedBacktestEngine, BacktestTimeConfig
from data_manager import DataManager
from data_fetcher import get_index_constituents
from config_manager import ConfigManager

app = Flask(__name__)
CORS(app)

# 初始化数据管理器和参数配置管理器
manager = DataManager()
config_manager = ConfigManager()

# 后台任务状态
background_tasks = {}

@app.route('/')
def index():
    """主页"""
    return render_template('index_with_cache.html')

@app.route('/parameters')
def parameters_page():
    """参数配置页面"""
    return render_template('parameters_config.html')

@app.route('/parameters/visual')
def parameters_visual_page():
    """参数配置页面（可视化版本）"""
    return render_template('parameters_config_visual.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    return jsonify({
        'start_date': START_DATE,
        'end_date': END_DATE,
        'strategy_params': STRATEGY_PARAMS,
        'max_stocks': MAX_STOCKS,
    })

@app.route('/api/cache/status', methods=['GET'])
def get_cache_status():
    """获取缓存状态"""
    try:
        status = manager.get_cache_status()
        return jsonify({
            'success': True,
            'total_records': status['total_records'],
            'db_size': round(status['db_size'], 2),
            'db_file': status['db_file'],
            'update_logs': status['update_logs']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cache/fetch', methods=['POST'])
def fetch_data():
    """获取数据并缓存"""
    try:
        data = request.json
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({'success': False, 'error': '请输入股票代码'}), 400

        # 从网络获取并保存
        df = manager.fetch_and_cache(symbol, force_refresh=True)

        if df is not None and len(df) > 0:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'records': len(df),
                'start_date': str(df['日期'].min().date()),
                'end_date': str(df['日期'].max().date()),
                'message': f'成功获取 {len(df)} 条数据'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'无法获取 {symbol} 的数据'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cache/update', methods=['POST'])
def update_data():
    """更新股票数据（增量更新）"""
    try:
        data = request.json
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({'success': False, 'error': '请输入股票代码'}), 400

        # 后台更新
        result = manager.update_single_stock(symbol)

        if result:
            return jsonify({
                'success': True,
                'message': f'{symbol} 已更新'
            })
        else:
            return jsonify({
                'success': False,
                'error': '无新数据或更新失败'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """获取所有可用板块"""
    try:
        sectors_list = [
            {
                'key': key,
                'name': value['name'],
                'description': value['description']
            }
            for key, value in SECTORS.items()
        ]
        return jsonify({
            'success': True,
            'sectors': sectors_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cache/stocks', methods=['GET'])
def get_cached_stocks():
    """获取已缓存的股票列表（按板块分类）"""
    try:
        # 从数据管理器获取所有缓存的股票
        all_stocks = manager.get_all_cached_stocks()

        # 按板块分类
        by_sector = {
            '沪深A股': [],
            '创业板': [],
            '科创板': [],
            '深成指': [],
            '中证500': [],
            '其他': []
        }

        # 提前获取中证500列表（只调用一次，避免重复）
        zz500_set = set()
        try:
            zz500_list = get_index_constituents('000905', limit=None)
            zz500_set = set(zz500_list)
        except Exception as e:
            print(f"获取中证500列表失败: {e}")

        def categorize_stock(symbol: str, zz500_stocks: set) -> list:
            """返回股票所属的所有板块"""
            sectors = []

            # 创业板：300开头
            if symbol.startswith('300'):
                sectors.extend(['创业板', '深成指', '沪深A股'])
            # 科创板：688开头
            elif symbol.startswith('688'):
                sectors.extend(['科创板', '沪深A股'])
            # 深圳主板：000/001/002/003/004开头
            elif symbol.startswith(('000', '001', '002', '003', '004')):
                sectors.extend(['深成指', '沪深A股'])
            # 上海主板：6开头
            elif symbol.startswith('6'):
                sectors.append('沪深A股')
            else:
                sectors.append('其他')

            # 检查是否属于中证500
            if symbol in zz500_stocks:
                sectors.append('中证500')

            return sectors

        # 分类股票
        for stock in all_stocks:
            sectors = categorize_stock(stock, zz500_set)
            for sector in sectors:
                if sector in by_sector:
                    by_sector[sector].append(stock)

        # 去重并排序
        for sector in by_sector:
            by_sector[sector] = sorted(list(set(by_sector[sector])))

        # 移除空的板块
        by_sector = {k: v for k, v in by_sector.items() if v}

        return jsonify({
            'success': True,
            'total': len(all_stocks),
            'stocks': sorted(all_stocks),
            'by_sector': by_sector
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cache/batch-fetch', methods=['POST'])
def batch_fetch_data():
    """批量获取数据"""
    try:
        # 获取指数成分股
        index_code = "000905"  # 中证500
        stocks = get_index_constituents(index_code, limit=MAX_STOCKS)

        if not stocks:
            return jsonify({'success': False, 'error': '无法获取成分股'}), 400

        # 后台批量获取
        def fetch_batch():
            manager.batch_fetch_and_cache(stocks, force_refresh=False)

        # 如果支持后台任务
        task_id = f'batch_fetch_{int(datetime.now().timestamp())}'
        background_tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'total': len(stocks)
        }

        thread = threading.Thread(target=fetch_batch)
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'stocks': stocks,
            'message': '已开始批量获取，请稍候...'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cache/batch-fetch-sector', methods=['POST'])
def batch_fetch_sector_data():
    """按板块和时间范围批量获取数据 - 自动获取全部市场数据"""
    try:
        data = request.json
        sector = data.get('sector', '中证500')
        start_date = data.get('start_date', START_DATE)
        end_date = data.get('end_date', END_DATE)
        # 移除用户输入的limit限制，自动获取全部可用数据
        limit = data.get('limit', None)  # 不限制，None = 获取全部

        # 获取板块对应的指数代码
        sector_info = SECTORS.get(sector)
        if not sector_info:
            return jsonify({'success': False, 'error': '选定的板块不支持，请重新选择'}), 400

        index_code = sector_info['code']

        # 获取指数成分股（自动获取全部）
        stocks = get_index_constituents(index_code, limit=limit)

        if not stocks:
            return jsonify({'success': False, 'error': '无法获取成分股列表，请检查网络连接'}), 400

        # 后台批量获取
        def fetch_sector_batch():
            try:
                manager.batch_fetch_and_cache(stocks, force_refresh=False)
            except Exception as e:
                background_tasks[task_id]['status'] = 'failed'
                background_tasks[task_id]['error'] = str(e)

        # 创建后台任务
        task_id = f'batch_sector_{sector}_{int(datetime.now().timestamp())}'
        background_tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'total': len(stocks),
            'sector': sector,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        }

        thread = threading.Thread(target=fetch_sector_batch)
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'sector': sector,
            'stocks_count': len(stocks),
            'start_date': start_date,
            'end_date': end_date,
            'stocks': stocks[:5] if stocks else [],  # 返回前5只股票预览
            'message': '已开始获取数据，请稍候...'
        })

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"❌ Error in batch_fetch_sector_data: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': error_msg}), 400

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """获取所有可用策略"""
    try:
        strategies = config_manager.get_strategy_list()
        current = config_manager.get_current_strategy()

        return jsonify({
            'success': True,
            'strategies': strategies,
            'current_strategy': current,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/strategies/current', methods=['GET', 'POST'])
def manage_current_strategy():
    """获取或设置当前策略"""
    try:
        if request.method == 'GET':
            current = config_manager.get_current_strategy()
            params = config_manager.get_params()
            return jsonify({
                'success': True,
                'strategy': current,
                'params': params,
            })

        elif request.method == 'POST':
            data = request.json
            strategy_key = data.get('strategy')

            success, message = config_manager.set_current_strategy(strategy_key)

            return jsonify({
                'success': success,
                'message': message,
                'new_params': config_manager.get_params() if success else {},
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/strategies/<strategy_key>/params', methods=['GET'])
def get_strategy_params_endpoint(strategy_key):
    """获取指定策略的参数"""
    try:
        params = config_manager.get_strategy_params(strategy_key)

        if not params:
            return jsonify({
                'success': False,
                'error': f'策略 {strategy_key} 不存在'
            }), 404

        return jsonify({
            'success': True,
            'strategy': strategy_key,
            'params': params,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/backtest/cache', methods=['POST'])
def run_backtest_with_cache():
    """使用本地缓存数据进行回测（支持策略选择）"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        strategy_key = data.get('strategy', None)  # 新增：允许指定策略
        custom_params = data.get('params', None)   # 新增：允许自定义参数

        # 确定使用的策略和参数
        if strategy_key is None:
            strategy_key = config_manager.get_current_strategy()

        if custom_params is None:
            params = config_manager.get_strategy_params(strategy_key)
        else:
            params = custom_params

        # 动态导入策略类
        strategy_classes = {
            'VolumeBreakoutStrategy': VolumeBreakoutStrategy,
            'SteadyTrendStrategy': SteadyTrendStrategy,
            'AggressiveMomentumStrategy': AggressiveMomentumStrategy,
            'BalancedMultiFactorStrategy': BalancedMultiFactorStrategy,
        }

        # 添加新策略（如果可用）
        if NEW_STRATEGIES_AVAILABLE:
            strategy_classes['DoubleMACrossStrategy'] = DoubleMACrossStrategy
            strategy_classes['GridTradingStrategy'] = GridTradingStrategy
            strategy_classes['TurtleTradingStrategy'] = TurtleTradingStrategy

        class_name = STRATEGY_MAP[strategy_key]['class_name']
        StrategyClass = strategy_classes[class_name]

        # 创建策略实例
        strategy = StrategyClass(params)

        if not symbols:
            # 使用所有缓存的数据
            pass

        # 加载缓存数据
        all_data = {}
        for symbol in symbols or ['000001']:  # 默认测试 000001
            df = manager.get_data_from_cache(symbol)
            if df is not None and len(df) > 0:
                all_data[symbol] = df

        if not all_data:
            return jsonify({
                'success': False,
                'error': '没有可用的缓存数据，请先获取数据'
            }), 400

        # 获取交易设置
        trading_settings = config_manager.get_trading_settings()

        # 运行回测 - 使用增强版引擎
        from config import DATA_FETCH_START, DATA_FETCH_END, BACKTEST_START, BACKTEST_END, MAX_POSITION_RATIO

        time_config = BacktestTimeConfig(
            data_start=DATA_FETCH_START,
            data_end=DATA_FETCH_END,
            backtest_start=BACKTEST_START,
            backtest_end=BACKTEST_END
        )

        engine = EnhancedBacktestEngine(
            initial_capital=trading_settings['initial_capital'],
            position_ratio=trading_settings['position_ratio'],
            commission_rate=trading_settings['commission_rate'],
            slippage=trading_settings['slippage'],
            time_config=time_config,
            max_position_ratio=MAX_POSITION_RATIO
        )
        results = engine.run_multiple_stocks_with_portfolio(all_data, strategy)

        # 提取投资组合总结
        portfolio_summary = results.get('portfolio_summary', {})
        stock_results = results.get('stock_results', {})
        trade_history = results.get('trade_history', [])
        initial_capital = portfolio_summary.get('initial_capital', 100000)

        # 从 trade_history 中提取每笔卖出交易的收益
        all_trades = []
        wins = 0
        prev_sell_cash = initial_capital

        for i, trade_record in enumerate(trade_history):
            if trade_record.get('action') == 'SELL':
                # 找配对的买入交易
                buy_index = i - 1
                while buy_index >= 0 and trade_record.get('symbol') != trade_history[buy_index].get('symbol'):
                    buy_index -= 1

                if buy_index >= 0:
                    buy_trade = trade_history[buy_index]
                    sell_trade = trade_record

                    # 从策略中获取更多信息
                    stock_trades = stock_results.get(trade_record.get('symbol'), {}).get('trades', [])
                    matching_trade = None
                    for st in stock_trades:
                        if (str(st.get('买入日期')).split()[0] == str(buy_trade['date']).split()[0] and
                            str(st.get('卖出日期')).split()[0] == str(sell_trade['date']).split()[0]):
                            matching_trade = st
                            break

                    # 计算这笔交易的收益贡献（相对于初始资金）
                    cash_after_sell = sell_trade.get('cash_after', 0)
                    trade_contribution = (cash_after_sell - prev_sell_cash) / initial_capital * 100

                    all_trades.append({
                        'symbol': trade_record.get('symbol'),
                        'buy_date': str(buy_trade['date']).split()[0],
                        'buy_price': round(buy_trade['price'], 2),
                        'sell_date': str(sell_trade['date']).split()[0],
                        'sell_price': round(sell_trade['price'], 2),
                        'return': round(trade_contribution, 4),  # 这笔交易的收益贡献
                        'status': matching_trade.get('状态', '平仓') if matching_trade else '平仓'
                    })

                    if trade_contribution > 0:
                        wins += 1

                    prev_sell_cash = cash_after_sell

        # 计算统计数据
        total_trades_count = len(all_trades)
        total_return_pct = portfolio_summary.get('total_return_pct', 0)

        # 平均收益率 = 总收益率 ÷ 交易笔数 (保持一致性)
        avg_return = total_return_pct / total_trades_count if total_trades_count > 0 else 0

        # 胜率 = 盈利交易数 ÷ 总交易数
        win_rate = (wins / total_trades_count * 100) if total_trades_count > 0 else 0

        return jsonify({
            'success': True,
            'strategy': strategy_key,
            'strategy_name': STRATEGY_MAP[strategy_key]['name'],
            'stocks_tested': len(all_data),
            'portfolio_summary': portfolio_summary,
            'total_trades': total_trades_count,
            'total_return': round(total_return_pct, 2),
            'avg_return': round(avg_return, 4),  # 保留4位小数，因为平均值很小
            'win_rate': round(win_rate, 1),
            'final_capital': round(portfolio_summary.get('final_total_value', 0), 2),
            'rejected_trades': portfolio_summary.get('num_trades_rejected', 0),
            'trades': all_trades[:20]  # 返回前20笔
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存"""
    try:
        data = request.json
        symbol = data.get('symbol')

        manager.clear_cache(symbol)

        return jsonify({
            'success': True,
            'message': f'已清空{"'" + symbol + "'" if symbol else "所有"}缓存'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    """获取参数配置信息"""
    try:
        info = config_manager.get_config_info()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/parameters/update', methods=['POST'])
def update_parameters():
    """更新参数"""
    try:
        data = request.json
        params = data.get('params', {})

        # 验证参数
        validation = config_manager.validate_params(params)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['message']
            }), 400

        # 更新参数
        success, message = config_manager.update_params(params)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'new_params': config_manager.get_params()
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/parameters/reset', methods=['POST'])
def reset_parameters():
    """重置为默认参数"""
    try:
        success, message = config_manager.reset_to_default()

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'new_params': config_manager.get_params()
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/parameters/preset', methods=['GET', 'POST', 'DELETE'])
def manage_preset():
    """管理参数预设"""
    try:
        if request.method == 'GET':
            # 列出所有预设
            presets = config_manager.get_all_presets()
            return jsonify({
                'success': True,
                'presets': presets
            })

        elif request.method == 'POST':
            # 保存或加载预设
            data = request.json
            action = data.get('action')

            if action == 'save':
                preset_name = data.get('name')
                if not preset_name:
                    return jsonify({
                        'success': False,
                        'error': '预设名称不能为空'
                    }), 400

                if config_manager.export_preset(preset_name, config_manager.get_params()):
                    return jsonify({
                        'success': True,
                        'message': f'✓ 预设 "{preset_name}" 已保存'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '保存预设失败'
                    }), 400

            elif action == 'load':
                preset_name = data.get('name')
                if not preset_name:
                    return jsonify({
                        'success': False,
                        'error': '预设名称不能为空'
                    }), 400

                success, result = config_manager.load_preset(preset_name)
                if success:
                    config_manager.update_params(result)
                    return jsonify({
                        'success': True,
                        'message': f'✓ 已加载预设 "{preset_name}"',
                        'new_params': config_manager.get_params()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result
                    }), 400

        elif request.method == 'DELETE':
            # 删除预设
            data = request.json
            preset_name = data.get('name')

            presets = config_manager.get_all_presets()
            if preset_name in presets:
                del presets[preset_name]
                import json
                from pathlib import Path
                with open(Path("./strategy_presets.json"), 'w', encoding='utf-8') as f:
                    json.dump(presets, f, ensure_ascii=False, indent=2)
                return jsonify({
                    'success': True,
                    'message': f'✓ 预设 "{preset_name}" 已删除'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '预设不存在'
                }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/backtest/export-trades', methods=['POST'])
def export_trades_to_excel():
    """导出回测交易记录到Excel"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        strategy_key = data.get('strategy', None)
        custom_params = data.get('params', None)

        # 确定使用的策略和参数
        if strategy_key is None:
            strategy_key = config_manager.get_current_strategy()

        if custom_params is None:
            params = config_manager.get_strategy_params(strategy_key)
        else:
            params = custom_params

        # 动态导入策略类
        strategy_classes = {
            'VolumeBreakoutStrategy': VolumeBreakoutStrategy,
            'SteadyTrendStrategy': SteadyTrendStrategy,
            'AggressiveMomentumStrategy': AggressiveMomentumStrategy,
            'BalancedMultiFactorStrategy': BalancedMultiFactorStrategy,
        }

        # 添加新策略（如果可用）
        if NEW_STRATEGIES_AVAILABLE:
            strategy_classes['DoubleMACrossStrategy'] = DoubleMACrossStrategy
            strategy_classes['GridTradingStrategy'] = GridTradingStrategy
            strategy_classes['TurtleTradingStrategy'] = TurtleTradingStrategy

        class_name = STRATEGY_MAP[strategy_key]['class_name']
        StrategyClass = strategy_classes[class_name]

        # 创建策略实例
        strategy = StrategyClass(params)

        if not symbols:
            return jsonify({
                'success': False,
                'error': '没有可导出的股票数据'
            }), 400

        # 加载缓存数据并运行回测
        all_data = {}
        for symbol in symbols:
            df = manager.get_data_from_cache(symbol)
            if df is not None and len(df) > 0:
                all_data[symbol] = df

        if not all_data:
            return jsonify({
                'success': False,
                'error': '没有可用的缓存数据'
            }), 400

        # 获取交易设置
        trading_settings = config_manager.get_trading_settings()

        # 运行回测 - 使用增强版引擎
        from config import DATA_FETCH_START, DATA_FETCH_END, BACKTEST_START, BACKTEST_END, MAX_POSITION_RATIO

        time_config = BacktestTimeConfig(
            data_start=DATA_FETCH_START,
            data_end=DATA_FETCH_END,
            backtest_start=BACKTEST_START,
            backtest_end=BACKTEST_END
        )

        engine = EnhancedBacktestEngine(
            initial_capital=trading_settings['initial_capital'],
            position_ratio=trading_settings['position_ratio'],
            commission_rate=trading_settings['commission_rate'],
            slippage=trading_settings['slippage'],
            time_config=time_config,
            max_position_ratio=MAX_POSITION_RATIO
        )
        results = engine.run_multiple_stocks_with_portfolio(all_data, strategy)

        # 生成Excel文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'回测交易明细_{timestamp}.xlsx'
        filepath = os.path.join(os.getcwd(), filename)

        # 使用现有的导出函数
        export_batch_results_to_excel(results, output_file=filepath)

        # 发送文件
        return send_file(
            filepath,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'cache_status': manager.get_cache_status()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
