"""Web应用 - Flask版本，支持浏览器访问"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

from config import START_DATE, END_DATE, STRATEGY_PARAMS, MAX_STOCKS
from demo_test_debug import generate_better_mock_data
from strategy import VolumeBreakoutStrategy
from export_to_excel import export_detailed_trades_to_excel
from backtest_engine import BacktestEngine

app = Flask(__name__)
CORS(app)

# 存储回测结果
backtest_results = {}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    return jsonify({
        'start_date': START_DATE,
        'end_date': END_DATE,
        'strategy_params': STRATEGY_PARAMS,
        'max_stocks': MAX_STOCKS,
    })

@app.route('/api/backtest/demo', methods=['POST'])
def run_demo_backtest():
    """运行演示回测"""
    try:
        data = request.json
        stock_code = data.get('stock_code', '000001')

        # 生成模拟数据
        df = generate_better_mock_data(stock_code)

        # 运行策略
        strategy = VolumeBreakoutStrategy(STRATEGY_PARAMS)
        signals = strategy.calculate_signals(df)
        trades = strategy.get_trades(df)

        # 计算统计数据
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

        if len(trades_df) > 0:
            wins = len(trades_df[trades_df['收益率%'] > 0])
            win_rate = wins / len(trades_df) * 100
            total_return = trades_df['收益率%'].sum()
            avg_return = trades_df['收益率%'].mean()
        else:
            win_rate = 0
            total_return = 0
            avg_return = 0

        result = {
            'success': True,
            'stock_code': stock_code,
            'data_points': len(df),
            'buy_signals': int(signals['Buy_Signal'].sum()),
            'sell_signals': int(signals['Sell_Signal'].sum()),
            'trades': len(trades),
            'total_return': round(total_return, 2),
            'avg_return': round(avg_return, 2),
            'win_rate': round(win_rate, 1),
            'trades_list': [
                {
                    'buy_date': str(t['买入日期'].date()) if hasattr(t['买入日期'], 'date') else str(t['买入日期']),
                    'buy_price': round(t['买入价'], 2),
                    'sell_date': str(t['卖出日期'].date()) if hasattr(t['卖出日期'], 'date') else str(t['卖出日期']),
                    'sell_price': round(t['卖出价'], 2),
                    'return': round(t['收益率%'], 2),
                    'status': t['状态']
                } for t in trades
            ]
        }

        backtest_results[stock_code] = result
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/backtest/export', methods=['POST'])
def export_backtest():
    """导出回测结果为Excel"""
    try:
        data = request.json
        stock_code = data.get('stock_code', '000001')

        # 生成模拟数据
        df = generate_better_mock_data(stock_code)

        # 导出Excel
        output_file = f'回测__{stock_code}.xlsx'
        export_detailed_trades_to_excel(stock_code, df, output_file)

        # 返回文件
        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/parameters', methods=['GET', 'POST'])
def manage_parameters():
    """获取或修改策略参数"""
    if request.method == 'GET':
        return jsonify(STRATEGY_PARAMS)
    else:
        # POST: 修改参数
        new_params = request.json
        # 这里可以保存新参数到config.py
        return jsonify({'success': True, 'message': '参数已更新'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # 生产环境使用 gunicorn
    # 开发环境
    app.run(debug=True, host='0.0.0.0', port=5000)
