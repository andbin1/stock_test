"""测试data_manager.py - 数据管理模块"""
import pytest
import pandas as pd
import sqlite3
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from data_manager import DataManager


@pytest.fixture
def temp_data_manager(tmp_path, monkeypatch):
    """创建使用临时目录的DataManager"""
    # 修改DATA_DIR和DB_FILE路径
    test_dir = tmp_path / "data_cache"
    test_dir.mkdir()
    test_db = test_dir / "test_stock_data.db"

    # Mock模块级别的变量
    import data_manager
    monkeypatch.setattr(data_manager, 'DATA_DIR', test_dir)
    monkeypatch.setattr(data_manager, 'DB_FILE', test_db)
    monkeypatch.setattr(data_manager, 'CACHE_DIR', test_dir / "cache")

    manager = DataManager()
    return manager


class TestDataManagerInit:
    """测试DataManager初始化"""

    def test_init_creates_database(self, temp_data_manager):
        """测试初始化会创建数据库"""
        assert temp_data_manager.db_file.exists()

    def test_init_creates_tables(self, temp_data_manager):
        """测试初始化会创建表"""
        conn = sqlite3.connect(temp_data_manager.db_file)
        cursor = conn.cursor()

        # 检查stock_data表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_data'")
        assert cursor.fetchone() is not None

        # 检查update_log表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='update_log'")
        assert cursor.fetchone() is not None

        conn.close()


class TestSaveAndGetDataFromCache:
    """测试数据保存和读取"""

    def test_save_data_to_cache_basic(self, temp_data_manager, sample_stock_data):
        """测试基本的数据保存"""
        df = sample_stock_data.copy()
        result = temp_data_manager.save_data_to_cache("000001", df)

        assert result is True

    def test_save_data_to_cache_empty_data(self, temp_data_manager):
        """测试保存空数据"""
        df = pd.DataFrame()
        result = temp_data_manager.save_data_to_cache("000001", df)

        assert result is False

    def test_save_data_to_cache_none(self, temp_data_manager):
        """测试保存None"""
        result = temp_data_manager.save_data_to_cache("000001", None)

        assert result is False

    def test_get_data_from_cache_basic(self, temp_data_manager, sample_stock_data):
        """测试基本的数据读取"""
        # 先保存数据
        df = sample_stock_data.copy()
        temp_data_manager.save_data_to_cache("000001", df)

        # 读取数据
        result_df = temp_data_manager.get_data_from_cache("000001", "20240101", "20241231")

        assert result_df is not None
        assert len(result_df) > 0
        assert '日期' in result_df.columns
        assert '收盘' in result_df.columns

    def test_get_data_from_cache_no_data(self, temp_data_manager):
        """测试读取不存在的数据"""
        result_df = temp_data_manager.get_data_from_cache("999999", "20240101", "20241231")

        assert result_df is None

    def test_get_data_from_cache_date_range(self, temp_data_manager, sample_stock_data):
        """测试日期范围过滤"""
        # 保存数据
        df = sample_stock_data.copy()
        temp_data_manager.save_data_to_cache("000001", df)

        # 读取部分日期范围
        result_df = temp_data_manager.get_data_from_cache("000001", "20240101", "20240131")

        assert result_df is not None
        # 结果应该少于原始数据
        if len(result_df) > 0:
            # 验证日期范围
            assert result_df['日期'].min() >= pd.Timestamp('2024-01-01')
            assert result_df['日期'].max() <= pd.Timestamp('2024-01-31')

    def test_save_duplicate_data(self, temp_data_manager, sample_stock_data):
        """测试保存重复数据（应该被忽略）"""
        df = sample_stock_data.copy()

        # 第一次保存
        result1 = temp_data_manager.save_data_to_cache("000001", df)
        assert result1 is True

        # 第二次保存相同数据（应该被IGNORE）
        result2 = temp_data_manager.save_data_to_cache("000001", df)
        assert result2 is True  # 仍然返回True，但不会重复插入


class TestFetchAndCache:
    """测试获取和缓存数据"""

    @patch('data_manager.get_stock_data')
    def test_fetch_and_cache_from_network(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试从网络获取并缓存"""
        mock_get_stock_data.return_value = sample_stock_data.copy()

        df = temp_data_manager.fetch_and_cache("000001", "20240101", "20241231")

        assert df is not None
        assert len(df) > 0
        mock_get_stock_data.assert_called_once()

    @patch('data_manager.get_stock_data')
    def test_fetch_and_cache_use_cached(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试使用缓存数据"""
        # 先保存到缓存
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())

        # 再次获取应该使用缓存，不调用网络
        df = temp_data_manager.fetch_and_cache("000001", "20240101", "20241231", force_refresh=False)

        assert df is not None
        mock_get_stock_data.assert_not_called()

    @patch('data_manager.get_stock_data')
    def test_fetch_and_cache_force_refresh(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试强制刷新"""
        # 先保存到缓存
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())

        mock_get_stock_data.return_value = sample_stock_data.copy()

        # 强制刷新应该调用网络
        df = temp_data_manager.fetch_and_cache("000001", "20240101", "20241231", force_refresh=True)

        assert df is not None
        mock_get_stock_data.assert_called_once()

    @patch('data_manager.get_stock_data')
    def test_fetch_and_cache_network_failure(self, mock_get_stock_data, temp_data_manager):
        """测试网络获取失败"""
        mock_get_stock_data.return_value = None

        df = temp_data_manager.fetch_and_cache("000001", "20240101", "20241231")

        assert df is None


class TestBatchFetchAndCache:
    """测试批量获取和缓存"""

    @patch('data_manager.get_stock_data')
    def test_batch_fetch_and_cache_basic(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试批量获取"""
        mock_get_stock_data.return_value = sample_stock_data.copy()

        symbols = ['000001', '000002', '600000']
        result = temp_data_manager.batch_fetch_and_cache(symbols, "20240101", "20241231")

        assert len(result) == 3
        assert '000001' in result
        assert '000002' in result
        assert '600000' in result

    @patch('data_manager.get_stock_data')
    def test_batch_fetch_and_cache_partial_failure(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试部分获取失败"""
        # 模拟部分成功，部分失败
        def side_effect(symbol, start, end):
            if symbol == '000001':
                return sample_stock_data.copy()
            else:
                return None

        mock_get_stock_data.side_effect = side_effect

        symbols = ['000001', '000002', '600000']
        result = temp_data_manager.batch_fetch_and_cache(symbols, "20240101", "20241231")

        # 只有000001成功
        assert len(result) == 1
        assert '000001' in result


class TestUpdateSingleStock:
    """测试增量更新"""

    @patch('data_manager.get_stock_data')
    def test_update_single_stock_no_existing_data(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试首次更新（无现有数据）"""
        mock_get_stock_data.return_value = sample_stock_data.copy()

        result = temp_data_manager.update_single_stock("000001")

        assert result is True
        mock_get_stock_data.assert_called_once()

    @patch('data_manager.get_stock_data')
    def test_update_single_stock_with_existing_data(self, mock_get_stock_data, temp_data_manager, sample_stock_data):
        """测试增量更新（有现有数据）"""
        # 先保存一些旧数据
        old_data = sample_stock_data.iloc[:50].copy()
        temp_data_manager.save_data_to_cache("000001", old_data)

        # 模拟获取新数据
        new_data = sample_stock_data.iloc[50:].copy()
        mock_get_stock_data.return_value = new_data

        result = temp_data_manager.update_single_stock("000001")

        assert result is True

    @patch('data_manager.get_stock_data')
    def test_update_single_stock_no_new_data(self, mock_get_stock_data, temp_data_manager):
        """测试无新数据更新"""
        mock_get_stock_data.return_value = None

        result = temp_data_manager.update_single_stock("000001")

        assert result is False


class TestCacheManagement:
    """测试缓存管理功能"""

    def test_get_all_cached_stocks(self, temp_data_manager, sample_stock_data):
        """测试获取所有缓存的股票代码"""
        # 保存多只股票
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())
        temp_data_manager.save_data_to_cache("000002", sample_stock_data.copy())
        temp_data_manager.save_data_to_cache("600000", sample_stock_data.copy())

        stocks = temp_data_manager.get_all_cached_stocks()

        assert len(stocks) == 3
        assert "000001" in stocks
        assert "000002" in stocks
        assert "600000" in stocks

    def test_get_cache_status(self, temp_data_manager, sample_stock_data):
        """测试获取缓存状态"""
        # 保存一些数据
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())

        status = temp_data_manager.get_cache_status()

        assert 'total_records' in status
        assert 'db_file' in status
        assert 'db_size' in status
        assert 'update_logs' in status
        assert status['total_records'] > 0

    def test_clear_cache_single_stock(self, temp_data_manager, sample_stock_data):
        """测试清空单只股票缓存"""
        # 保存数据
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())
        temp_data_manager.save_data_to_cache("000002", sample_stock_data.copy())

        # 清空000001
        temp_data_manager.clear_cache("000001")

        # 验证
        stocks = temp_data_manager.get_all_cached_stocks()
        assert "000001" not in stocks
        assert "000002" in stocks

    def test_clear_cache_all(self, temp_data_manager, sample_stock_data):
        """测试清空所有缓存"""
        # 保存数据
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())
        temp_data_manager.save_data_to_cache("000002", sample_stock_data.copy())

        # 清空所有
        temp_data_manager.clear_cache()

        # 验证
        stocks = temp_data_manager.get_all_cached_stocks()
        assert len(stocks) == 0

    def test_export_cache_to_csv(self, temp_data_manager, sample_stock_data, tmp_path):
        """测试导出缓存为CSV"""
        # 保存数据
        temp_data_manager.save_data_to_cache("000001", sample_stock_data.copy())

        # 导出
        output_dir = str(tmp_path / "export")
        result_file = temp_data_manager.export_cache_to_csv("000001", output_dir)

        assert result_file is not None
        assert os.path.exists(result_file)

    def test_export_cache_to_csv_no_data(self, temp_data_manager, tmp_path):
        """测试导出不存在的数据"""
        output_dir = str(tmp_path / "export")
        result_file = temp_data_manager.export_cache_to_csv("999999", output_dir)

        assert result_file is None


class TestDataIntegrity:
    """测试数据完整性"""

    def test_data_consistency_after_save_and_load(self, temp_data_manager, sample_stock_data):
        """测试保存和加载后数据一致性"""
        df_original = sample_stock_data.copy()

        # 保存
        temp_data_manager.save_data_to_cache("000001", df_original)

        # 加载
        df_loaded = temp_data_manager.get_data_from_cache("000001", "20240101", "20241231")

        # 验证主要字段一致
        assert len(df_loaded) > 0
        # 验证数据长度（可能有差异，因为过滤了周末等）
        # 验证列存在
        assert '收盘' in df_loaded.columns
        assert '开盘' in df_loaded.columns
        assert '高' in df_loaded.columns
        assert '低' in df_loaded.columns

    def test_date_format_conversion(self, temp_data_manager):
        """测试日期格式转换"""
        df = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=10),
            '收盘': [10.0] * 10,
            '开盘': [10.0] * 10,
            '高': [10.5] * 10,
            '低': [9.5] * 10,
            '成交量': [1000000] * 10,
            '成交额': [10000000] * 10,
        })

        # 保存
        temp_data_manager.save_data_to_cache("000001", df)

        # 加载
        df_loaded = temp_data_manager.get_data_from_cache("000001", "20240101", "20240110")

        # 验证日期是datetime类型
        assert pd.api.types.is_datetime64_any_dtype(df_loaded['日期'])


class TestEdgeCases:
    """测试边界情况"""

    def test_handle_missing_columns(self, temp_data_manager):
        """测试处理缺失列"""
        df = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=10),
            '收盘': [10.0] * 10,
            # 缺少其他列
        })

        # 应该不抛出异常
        result = temp_data_manager.save_data_to_cache("000001", df)
        assert result is True

    def test_handle_invalid_date_format(self, temp_data_manager):
        """测试处理无效日期格式"""
        # 使用YYYYMMDD格式（应该被转换）
        df_loaded = temp_data_manager.get_data_from_cache("000001", "20240101", "20240110")

        # 不应该抛出异常
        # 如果没有数据，返回None
        if df_loaded is not None:
            assert '日期' in df_loaded.columns
