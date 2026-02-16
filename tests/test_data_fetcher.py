"""测试data_fetcher.py - 数据获取模块"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from data_fetcher import (
    generate_stock_codes,
    get_index_constituents,
    get_stock_data,
    get_batch_stock_data,
)


class TestGenerateStockCodes:
    """测试股票代码生成"""

    def test_generate_stock_codes_basic(self):
        """测试基本的代码生成"""
        codes = generate_stock_codes("000", 1, 5)

        assert len(codes) == 5
        assert codes == ["000001", "000002", "000003", "000004", "000005"]

    def test_generate_stock_codes_different_prefix(self):
        """测试不同的前缀"""
        codes = generate_stock_codes("600", 0, 3)

        assert len(codes) == 4
        assert codes == ["600000", "600001", "600002", "600003"]

    def test_generate_stock_codes_single(self):
        """测试生成单个代码"""
        codes = generate_stock_codes("300", 100, 100)

        assert len(codes) == 1
        assert codes == ["300100"]

    def test_generate_stock_codes_large_range(self):
        """测试大范围生成"""
        codes = generate_stock_codes("000", 1, 999)

        assert len(codes) == 999
        assert codes[0] == "000001"
        assert codes[-1] == "000999"


class TestGetIndexConstituents:
    """测试获取指数成分股"""

    def test_get_index_constituents_sz_a_stock(self):
        """测试获取沪深A股"""
        stocks = get_index_constituents("000001")

        assert len(stocks) > 0
        # 应该包含深圳主板、创业板和上海主板
        assert any(s.startswith("000") for s in stocks)
        assert any(s.startswith("300") for s in stocks)
        assert any(s.startswith("600") for s in stocks)

    def test_get_index_constituents_cyb(self):
        """测试获取创业板"""
        stocks = get_index_constituents("399006")

        assert len(stocks) > 0
        # 只应该包含300开头的
        assert all(s.startswith("300") for s in stocks)

    def test_get_index_constituents_kcb(self):
        """测试获取科创板"""
        stocks = get_index_constituents("000688")

        assert len(stocks) > 0
        # 只应该包含688开头的
        assert all(s.startswith("688") for s in stocks)

    def test_get_index_constituents_with_limit(self):
        """测试限制数量"""
        stocks = get_index_constituents("000001", limit=10)

        assert len(stocks) == 10

    def test_get_index_constituents_no_duplicates(self):
        """测试没有重复代码"""
        stocks = get_index_constituents("000001")

        # 转换为set后长度应该相同
        assert len(stocks) == len(set(stocks))

    def test_get_index_constituents_unsupported_index(self):
        """测试不支持的指数"""
        stocks = get_index_constituents("999999")

        # 应该返回默认列表
        assert len(stocks) > 0
        assert isinstance(stocks, list)


class TestGetStockData:
    """测试获取单只股票数据"""

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_get_stock_data_with_efinance(self, mock_ef_get):
        """测试使用efinance获取数据"""
        # Mock返回数据
        mock_df = pd.DataFrame({
            'column0': pd.date_range('2024-01-01', periods=10),
            'column1': [10.0] * 10,  # 开盘
            'column2': [10.5] * 10,  # 收盘
            'column3': [11.0] * 10,  # 高
            'column4': [9.5] * 10,   # 低
            'column5': [1000000] * 10,  # 成交量
            'column6': [10000000] * 10,  # 成交额
        })
        mock_ef_get.return_value = mock_df

        result = get_stock_data("000001", "20240101", "20240110")

        assert result is not None
        assert len(result) == 10
        assert '日期' in result.columns
        assert '收盘' in result.columns

    @patch('data_fetcher.HAS_EFINANCE', False)
    def test_get_stock_data_no_efinance(self):
        """测试没有efinance时的处理"""
        result = get_stock_data("000001", "20240101", "20240110")

        # 没有efinance应该返回None
        assert result is None

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_get_stock_data_empty_result(self, mock_ef_get):
        """测试空结果"""
        mock_ef_get.return_value = pd.DataFrame()

        result = get_stock_data("000001", "20240101", "20240110")

        assert result is None

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_get_stock_data_none_result(self, mock_ef_get):
        """测试None结果"""
        mock_ef_get.return_value = None

        result = get_stock_data("000001", "20240101", "20240110")

        assert result is None

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_get_stock_data_exception_handling(self, mock_ef_get):
        """测试异常处理"""
        mock_ef_get.side_effect = Exception("Network error")

        # 应该不抛出异常，而是返回None
        result = get_stock_data("000001", "20240101", "20240110")

        # 异常时应该返回None
        assert result is None

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_get_stock_data_retry_mechanism(self, mock_ef_get):
        """测试重试机制"""
        # 前两次失败，第三次成功
        mock_df = pd.DataFrame({
            '股票名称': ['测试股票'] * 10,
            '股票代码': ['000001'] * 10,
            '成交量': [100000000] * 10,
            '成交额': [10000000] * 10,
            '振幅': [2.0] * 10,
            '涨跌幅': [1.0] * 10,
            '涨跌额': [0.1] * 10,
            '换手率': [2.0] * 10,
        })

        mock_ak_get.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            mock_df
        ]

        result = get_stock_data("000001", "20240101", "20240110", max_retries=3)

        assert result is not None
        assert mock_ak_get.call_count == 3


class TestGetBatchStockData:
    """测试批量获取股票数据"""

    @patch('data_fetcher.get_stock_data')
    def test_get_batch_stock_data_basic(self, mock_get_stock):
        """测试基本的批量获取"""
        mock_df = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=10),
            '收盘': [10.0] * 10,
        })
        mock_get_stock.return_value = mock_df

        symbols = ['000001', '000002', '600000']
        result = get_batch_stock_data(symbols, "20240101", "20240110")

        assert len(result) == 3
        assert '000001' in result
        assert '000002' in result
        assert '600000' in result

    @patch('data_fetcher.get_stock_data')
    def test_get_batch_stock_data_partial_failure(self, mock_get_stock):
        """测试部分失败"""
        mock_df = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=10),
            '收盘': [10.0] * 10,
        })

        # 第二个失败
        def side_effect(symbol, start, end):
            if symbol == '000002':
                return None
            return mock_df

        mock_get_stock.side_effect = side_effect

        symbols = ['000001', '000002', '600000']
        result = get_batch_stock_data(symbols, "20240101", "20240110")

        assert len(result) == 2
        assert '000001' in result
        assert '000002' not in result
        assert '600000' in result

    @patch('data_fetcher.get_stock_data')
    def test_get_batch_stock_data_all_failure(self, mock_get_stock):
        """测试全部失败"""
        mock_get_stock.return_value = None

        symbols = ['000001', '000002', '600000']
        result = get_batch_stock_data(symbols, "20240101", "20240110")

        assert len(result) == 0

    @patch('data_fetcher.get_stock_data')
    def test_get_batch_stock_data_empty_symbol_list(self, mock_get_stock):
        """测试空股票列表"""
        result = get_batch_stock_data([], "20240101", "20240110")

        assert len(result) == 0
        mock_get_stock.assert_not_called()


class TestDataQuality:
    """测试数据质量"""

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_data_sorted_by_date(self, mock_ef_get):
        """测试数据按日期排序"""
        # 创建乱序的数据
        mock_df = pd.DataFrame({
            'column0': pd.to_datetime(['2024-01-05', '2024-01-03', '2024-01-01', '2024-01-04']),
            'column1': [10.0] * 4,
            'column2': [10.5] * 4,
            'column3': [11.0] * 4,
            'column4': [9.5] * 4,
            'column5': [1000000] * 4,
            'column6': [10000000] * 4,
        })
        mock_ef_get.return_value = mock_df

        result = get_stock_data("000001", "20240101", "20240110")

        # 验证排序
        dates = pd.to_datetime(result['日期'])
        assert (dates == dates.sort_values()).all()

    @patch('data_fetcher.ef.stock.get_quote_history')
    def test_data_no_null_close_price(self, mock_ef_get):
        """测试收盘价不为空"""
        mock_df = pd.DataFrame({
            'column0': pd.date_range('2024-01-01', periods=10),
            'column1': [10.0] * 10,
            'column2': [10.5, None, 10.6, None, 10.7, 10.8, None, 10.9, 11.0, 11.1],  # 有空值
            'column3': [11.0] * 10,
            'column4': [9.5] * 10,
            'column5': [1000000] * 10,
            'column6': [10000000] * 10,
        })
        mock_ef_get.return_value = mock_df

        result = get_stock_data("000001", "20240101", "20240110")

        # 应该过滤掉收盘价为空的行
        assert result['收盘'].notna().all()
        assert len(result) < 10  # 应该少于原始数据


class TestEdgeCases:
    """测试边界情况"""

    def test_generate_stock_codes_invalid_range(self):
        """测试无效范围（开始大于结束）"""
        codes = generate_stock_codes("000", 5, 1)

        # 应该返回空列表
        assert len(codes) == 0

    @patch('data_fetcher.HAS_EFINANCE', False)
    def test_get_stock_data_no_data_source(self):
        """测试无可用数据源"""
        result = get_stock_data("000001", "20240101", "20240110")

        assert result is None
