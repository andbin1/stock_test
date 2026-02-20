"""数据管理模块 - 本地缓存和增量更新"""
import os
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import time

from data_fetcher import get_stock_data
from config import START_DATE, END_DATE

# 数据存储目录
DATA_DIR = Path("./data_cache")
DB_FILE = DATA_DIR / "stock_data.db"
CACHE_DIR = DATA_DIR / "cache"

# 创建必要的目录
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

class DataManager:
    """数据管理类 - 处理本地缓存和网络获取"""

    def __init__(self):
        self.db_file = DB_FILE
        self.db_timeout = 30.0  # 数据库连接超时时间（秒）
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()

        # 创建表：股票日线数据
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume REAL,
                amount REAL,
                amplitude REAL,
                pct_change REAL,
                change REAL,
                turnover_rate REAL,
                UNIQUE(symbol, date)
            )
        ''')

        # 创建表：更新记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                last_update TEXT,
                last_date TEXT,
                record_count INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def get_data_from_cache(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """从本地缓存获取数据"""
        if start_date is None:
            start_date = START_DATE
        if end_date is None:
            end_date = END_DATE

        # 转换日期格式从 YYYYMMDD 到 YYYY-MM-DD（用于数据库查询）
        def convert_date_format(date_str: str) -> str:
            """将 YYYYMMDD 格式转换为 YYYY-MM-DD 格式"""
            if len(date_str) == 8 and date_str.isdigit():
                return f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
            return date_str  # 已经是正确格式

        start_date = convert_date_format(start_date)
        end_date = convert_date_format(end_date)

        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        query = f'''
            SELECT * FROM stock_data
            WHERE symbol = ? AND date >= ? AND date <= ?
            ORDER BY date
        '''

        df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        conn.close()

        if df.empty:
            return None

        # 转换数据类型（添加错误处理）
        try:
            # 使用 errors='coerce' 将无效日期转换为 NaT，而不是抛出异常
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # 删除日期解析失败的行
            invalid_count = df['date'].isna().sum()
            if invalid_count > 0:
                print(f"警告: {symbol} 有 {invalid_count} 条记录的日期无效，已删除")
                df = df.dropna(subset=['date'])

            if df.empty:
                print(f"错误: {symbol} 所有记录的日期都无效")
                return None

        except Exception as e:
            print(f"错误: {symbol} 日期转换失败 - {e}")
            return None

        df = df.rename(columns={'date': '日期', 'close': '收盘', 'open': '开盘',
                                'high': '高', 'low': '低', 'volume': '成交量',
                                'amount': '成交额', 'amplitude': '振幅',
                                'pct_change': '涨跌幅', 'change': '涨跌',
                                'turnover_rate': '换手率'})

        return df

    def save_data_to_cache(self, symbol: str, df: pd.DataFrame):
        """将数据保存到本地缓存"""
        if df is None or df.empty:
            return False

        df = df.copy()

        # 标准化列名
        rename_map = {
            '日期': 'date', '收盘': 'close', '开盘': 'open',
            '高': 'high', '低': 'low', '成交量': 'volume',
            '成交额': 'amount', '振幅': 'amplitude',
            '涨跌幅': 'pct_change', '涨跌': 'change', '换手率': 'turnover_rate'
        }

        for old, new in rename_map.items():
            if old in df.columns:
                df = df.rename(columns={old: new})

        # 转换日期格式（添加错误处理）
        try:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # 删除日期无效的行
            invalid_count = df['date'].isna().sum()
            if invalid_count > 0:
                print(f"警告: {symbol} 准备保存的数据中有 {invalid_count} 条日期无效，已删除")
                df = df.dropna(subset=['date'])

            if df.empty:
                print(f"错误: {symbol} 没有有效的日期数据，取消保存")
                return False

            # 转换为字符串格式
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"错误: {symbol} 日期格式转换失败 - {e}")
            return False

        # 添加symbol列
        df['symbol'] = symbol

        # 提取需要的列（按照数据库表的顺序）
        cols_to_keep = ['symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount',
                        'amplitude', 'pct_change', 'change', 'turnover_rate']
        available_cols = [col for col in cols_to_keep if col in df.columns]

        # 填充缺失列为None
        for col in cols_to_keep:
            if col not in df.columns:
                df[col] = None

        df = df[cols_to_keep]

        # 保存到数据库（添加重试机制）
        max_retries = 3
        retry_delay = 1  # 秒

        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
                cursor = conn.cursor()

                # 逐行插入以处理UNIQUE约束
                for _, row in df.iterrows():
                    cursor.execute('''
                        INSERT OR IGNORE INTO stock_data
                        (symbol, date, open, close, high, low, volume, amount, amplitude, pct_change, change, turnover_rate)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', tuple(row))

                conn.commit()

                # 更新日志
                last_date = df['date'].max() if len(df) > 0 else None
                self._update_log(symbol, len(df), last_date)

                print(f"✓ {symbol}: 已保存 {len(df)} 条数据到本地缓存")
                conn.close()
                return True

            except sqlite3.OperationalError as e:
                # 数据库锁错误，进行重试
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    print(f"⚠️  {symbol}: 数据库被锁定，{retry_delay}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    try:
                        conn.rollback()
                        conn.close()
                    except:
                        pass
                    continue
                else:
                    print(f"✗ {symbol}: 保存失败 - {e}")
                    try:
                        conn.rollback()
                        conn.close()
                    except:
                        pass
                    return False

            except Exception as e:
                print(f"✗ {symbol}: 保存失败 - {e}")
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
                return False

        return False

    def _update_log(self, symbol: str, count: int, last_date: str = None):
        """更新日志表"""
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO update_log (symbol, last_update, last_date, record_count)
            VALUES (?, ?, ?, ?)
        ''', (symbol, datetime.now().isoformat(), last_date, count))

        conn.commit()
        conn.close()

    def _need_daily_update(self, symbol: str) -> bool:
        """
        检查是否需要每日更新

        规则：如果今天还没有更新过，返回True
        """
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT last_update FROM update_log WHERE symbol = ?
            ''', (symbol,))
            result = cursor.fetchone()

            if result is None:
                # 没有更新记录，需要更新
                return True

            last_update_str = result[0]
            if last_update_str:
                # 解析最后更新时间
                last_update = datetime.fromisoformat(last_update_str)
                today = datetime.now().date()

                # 如果最后更新不是今天，需要更新
                return last_update.date() < today
            else:
                return True

        except Exception as e:
            print(f"检查更新状态失败: {e}")
            return True  # 出错时保守地选择更新
        finally:
            conn.close()

    def fetch_and_cache(self, symbol: str, start_date: str = None, end_date: str = None,
                       force_refresh: bool = False, daily_update: bool = True) -> pd.DataFrame:
        """
        获取数据并缓存

        优先策略：
        1. 如果 force_refresh=True，强制从网络获取
        2. 如果 daily_update=True（默认），检查是否需要每日首次更新
        3. 如果本地有缓存且不需要更新，使用缓存
        4. 如果本地无缓存或需要更新，从网络获取并保存

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            force_refresh: 强制刷新（忽略缓存）
            daily_update: 启用每日首次更新检查
        """
        if start_date is None:
            start_date = START_DATE
        if end_date is None:
            end_date = END_DATE

        # 检查是否需要更新
        should_update = force_refresh or (daily_update and self._need_daily_update(symbol))

        # 尝试从缓存获取
        if not should_update:
            cached_df = self.get_data_from_cache(symbol, start_date, end_date)
            if cached_df is not None and len(cached_df) > 0:
                print(f"✓ {symbol}: 从本地缓存读取 {len(cached_df)} 条数据（今日已更新）")
                return cached_df

        # 从网络获取
        update_reason = "强制刷新" if force_refresh else "每日首次更新"
        print(f"⏳ {symbol}: 正在从网络获取数据...（{update_reason}）")
        df = get_stock_data(symbol, start_date, end_date)

        if df is not None and len(df) > 0:
            self.save_data_to_cache(symbol, df)
            return df
        else:
            print(f"✗ {symbol}: 无法获取数据，尝试使用缓存")
            # 如果网络获取失败，尝试返回缓存数据
            cached_df = self.get_data_from_cache(symbol, start_date, end_date)
            return cached_df

    def batch_fetch_and_cache(self, symbols: list, start_date: str = None,
                             end_date: str = None, force_refresh: bool = False) -> dict:
        """批量获取和缓存数据"""
        all_data = {}
        failed = []

        for symbol in symbols:
            df = self.fetch_and_cache(symbol, start_date, end_date, force_refresh)
            if df is not None and len(df) > 0:
                all_data[symbol] = df
            else:
                failed.append(symbol)

        print(f"\n📊 批量获取结果: 成功 {len(all_data)}, 失败 {len(failed)}")
        return all_data

    def update_single_stock(self, symbol: str) -> bool:
        """更新单只股票的数据（增量更新）"""
        # 获取本地最新日期
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(date) FROM stock_data WHERE symbol = ?', (symbol,))
        result = cursor.fetchone()
        conn.close()

        if result[0]:
            # 从最后一个日期之后继续获取
            last_date = datetime.strptime(result[0], '%Y-%m-%d')
            new_start_date = (last_date + timedelta(days=1)).strftime('%Y%m%d')
        else:
            # 首次获取
            new_start_date = START_DATE

        new_end_date = END_DATE

        print(f"📅 {symbol}: 从 {new_start_date} 更新到 {new_end_date}")

        # 获取新数据
        df = get_stock_data(symbol, new_start_date, new_end_date)

        if df is not None and len(df) > 0:
            self.save_data_to_cache(symbol, df)
            return True
        else:
            print(f"⚠️  {symbol}: 无新数据需要更新")
            return False

    def get_all_cached_stocks(self) -> list:
        """获取所有已缓存的股票代码列表"""
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()

        # 获取所有不同的股票代码
        cursor.execute('SELECT DISTINCT symbol FROM stock_data ORDER BY symbol')
        stocks = cursor.fetchall()

        conn.close()

        return [stock[0] for stock in stocks]

    def get_cache_status(self) -> dict:
        """获取缓存状态"""
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()

        # 获取总数据量
        cursor.execute('SELECT COUNT(*) FROM stock_data')
        total_records = cursor.fetchone()[0]

        # 获取更新日志
        cursor.execute('SELECT symbol, last_update, last_date, record_count FROM update_log ORDER BY last_update DESC')
        logs = cursor.fetchall()

        conn.close()

        return {
            'total_records': total_records,
            'db_file': str(self.db_file),
            'db_size': os.path.getsize(self.db_file) / 1024 / 1024,  # MB
            'update_logs': [
                {
                    'symbol': log[0],
                    'last_update': log[1],
                    'last_date': log[2],
                    'record_count': log[3]
                } for log in logs
            ]
        }

    def clear_cache(self, symbol: str = None):
        """清空缓存"""
        conn = sqlite3.connect(self.db_file, timeout=self.db_timeout)
        cursor = conn.cursor()

        if symbol:
            cursor.execute('DELETE FROM stock_data WHERE symbol = ?', (symbol,))
            cursor.execute('DELETE FROM update_log WHERE symbol = ?', (symbol,))
            print(f"✓ 已清空 {symbol} 的缓存数据")
        else:
            cursor.execute('DELETE FROM stock_data')
            cursor.execute('DELETE FROM update_log')
            print("✓ 已清空所有缓存数据")

        conn.commit()
        conn.close()

    def export_cache_to_csv(self, symbol: str, output_dir: str = "./data_export"):
        """导出缓存数据为CSV"""
        Path(output_dir).mkdir(exist_ok=True)

        df = self.get_data_from_cache(symbol)
        if df is None or df.empty:
            print(f"✗ {symbol}: 无缓存数据")
            return None

        output_file = Path(output_dir) / f"{symbol}_data.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 已导出到: {output_file}")
        return str(output_file)


# 命令行工具
if __name__ == "__main__":
    import sys

    manager = DataManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            # 查看缓存状态
            status = manager.get_cache_status()
            print("\n" + "="*60)
            print("  数据缓存状态")
            print("="*60)
            print(f"总数据量: {status['total_records']} 条")
            print(f"数据库文件: {status['db_file']}")
            print(f"数据库大小: {status['db_size']:.2f} MB")
            print()
            print("更新日志:")
            for log in status['update_logs']:
                print(f"  {log['symbol']}: {log['record_count']}条 (最后更新: {log['last_date']})")

        elif command == "update":
            # 更新单只股票
            if len(sys.argv) > 2:
                symbol = sys.argv[2]
                manager.update_single_stock(symbol)
            else:
                print("用法: python data_manager.py update <symbol>")

        elif command == "clear":
            # 清空缓存
            if len(sys.argv) > 2:
                symbol = sys.argv[2]
                manager.clear_cache(symbol)
            else:
                confirm = input("确定要清空所有缓存? (yes/no): ")
                if confirm.lower() == "yes":
                    manager.clear_cache()

        elif command == "export":
            # 导出数据
            if len(sys.argv) > 2:
                symbol = sys.argv[2]
                manager.export_cache_to_csv(symbol)
            else:
                print("用法: python data_manager.py export <symbol>")

        elif command == "fetch":
            # 从网络获取并缓存
            if len(sys.argv) > 2:
                symbol = sys.argv[2]
                df = manager.fetch_and_cache(symbol, force_refresh=True)
            else:
                print("用法: python data_manager.py fetch <symbol>")

    else:
        print("""
数据管理工具

用法:
  python data_manager.py status                    查看缓存状态
  python data_manager.py fetch <symbol>            获取并缓存数据
  python data_manager.py update <symbol>           增量更新数据
  python data_manager.py export <symbol>           导出为CSV
  python data_manager.py clear [symbol]            清空缓存

示例:
  python data_manager.py status
  python data_manager.py fetch 000001
  python data_manager.py update 000001
  python data_manager.py export 000001
  python data_manager.py clear 000001
        """)
