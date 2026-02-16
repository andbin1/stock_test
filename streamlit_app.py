"""Streamlit版本 - 可部署到Streamlit Cloud"""
import streamlit as st
import pandas as pd
from datetime import datetime

from config import START_DATE, END_DATE, STRATEGY_PARAMS
from demo_test_debug import generate_better_mock_data
from strategy import VolumeBreakoutStrategy
from export_to_excel import export_detailed_trades_to_excel

# 页面配置
st.set_page_config(
    page_title="A股交易策略回测",
    page_icon="📈",
    layout="wide"
)

# 标题
st.title("📈 A股交易策略回测系统")
st.markdown("**策略**: 30日均线向上 + 最近3日量能放大 + 5日线回踩 + 3日持有")

# 侧边栏 - 策略参数
with st.sidebar:
    st.header("⚙️ 策略参数")

    ma_period = st.slider("MA周期(天)", 20, 60, STRATEGY_PARAMS['ma_period'])
    volume_multiplier = st.slider("量能倍数", 1.0, 10.0, STRATEGY_PARAMS['volume_multiplier'], step=0.5)
    hold_days = st.slider("持有天数", 1, 10, STRATEGY_PARAMS['hold_days'])

    st.divider()

    st.markdown("**数据范围**")
    st.text(f"开始: {START_DATE}")
    st.text(f"结束: {END_DATE}")

# 主要内容
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 回测设置")
    stock_code = st.text_input("输入股票代码", value="000001", placeholder="如: 000001, 600000")

with col2:
    st.header("🎯 操作")
    run_button = st.button("🚀 运行回测", use_container_width=True)

# 运行回测
if run_button:
    if not stock_code:
        st.error("❌ 请输入股票代码")
    else:
        with st.spinner("⏳ 正在回测..."):
            # 生成模拟数据
            df = generate_better_mock_data(stock_code)

            # 创建策略参数
            params = {
                'ma_period': ma_period,
                'volume_multiplier': volume_multiplier,
                'hold_days': hold_days,
                'retest_period': 5,
                'recent_days': 5,
            }

            # 运行策略
            strategy = VolumeBreakoutStrategy(params)
            signals = strategy.calculate_signals(df)
            trades = strategy.get_trades(df)

            # 计算统计
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

            # 显示结果
            st.success("✅ 回测完成")

            # 关键指标
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("交易笔数", len(trades))

            with col2:
                color = "🟢" if total_return >= 0 else "🔴"
                st.metric(f"{color} 总收益", f"{total_return:.2f}%")

            with col3:
                st.metric("平均收益", f"{avg_return:.2f}%")

            with col4:
                st.metric("胜率", f"{win_rate:.1f}%")

            # 信号统计
            st.divider()
            col1, col2, col3 = st.columns(3)

            with col1:
                st.info(f"📈 买入信号: {signals['Buy_Signal'].sum()}")

            with col2:
                st.info(f"📉 卖出信号: {signals['Sell_Signal'].sum()}")

            with col3:
                st.info(f"📊 数据点: {len(df)}")

            # 交易明细
            st.divider()
            st.header("📋 交易明细")

            if len(trades_df) > 0:
                # 格式化交易数据
                display_trades = []
                for idx, trade in enumerate(trades, 1):
                    display_trades.append({
                        '序号': idx,
                        '买入日期': trade['买入日期'].strftime("%Y-%m-%d") if hasattr(trade['买入日期'], 'strftime') else str(trade['买入日期']),
                        '买入价': f"¥{trade['买入价']:.2f}",
                        '卖出日期': trade['卖出日期'].strftime("%Y-%m-%d") if hasattr(trade['卖出日期'], 'strftime') else str(trade['卖出日期']),
                        '卖出价': f"¥{trade['卖出价']:.2f}",
                        '收益率': f"{trade['收益率%']:+.2f}%",
                        '状态': trade['状态']
                    })

                trades_display_df = pd.DataFrame(display_trades)

                # 着色
                def color_return(val):
                    if '-%' in str(val):
                        return 'background-color: #ffcccc'
                    elif '+%' in str(val):
                        return 'background-color: #ccffcc'
                    return ''

                st.dataframe(
                    trades_display_df.style.applymap(color_return, subset=['收益率']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("⚠️ 未产生任何交易信号")

            # 导出功能
            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                # 导出为CSV
                csv_trades = trades_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载交易明细 (CSV)",
                    data=csv_trades,
                    file_name=f"交易明细_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            with col2:
                st.info("💡 提示: Excel导出请在Web应用中使用")

            # 显示部分信号详情
            st.divider()
            st.subheader("🔍 信号详情（前10行）")

            signal_detail = signals[signals['Buy_Signal'] | signals['Sell_Signal']].head(10).copy()
            signal_detail['日期'] = signal_detail['日期'].dt.strftime("%Y-%m-%d")

            display_cols = ['日期', '收盘', 'MA5', 'MA30', 'MA30_Up', 'Volume_Surge', 'MA5_Retest', 'Buy_Signal', 'Sell_Signal']
            available_cols = [col for col in display_cols if col in signal_detail.columns]

            st.dataframe(signal_detail[available_cols], use_container_width=True, hide_index=True)

# 页脚
st.divider()
st.markdown("""
---
### 📌 使用说明

1. **输入股票代码**: 任何A股代码 (如 000001, 600000)
2. **调整策略参数**: 左侧滑块自定义参数
3. **运行回测**: 点击"运行回测"按钮
4. **查看结果**: 实时显示交易明细和统计
5. **导出数据**: 下载CSV格式的交易记录

### 🎯 策略说明

- **30日均线向上**: MA30 > MA30前一天
- **量能放大**: 最近3日成交量和 > 20日均成交量 × 倍数
- **5日线回踩**: 收盘价 < MA5 且 > MA5×0.95
- **3日持有**: 满足条件后3个交易日卖出

### ⚠️ 免责声明

本工具仅供学习研究使用，不构成投资建议。过往表现不代表未来收益。
""")
