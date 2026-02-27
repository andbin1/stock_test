"""回测历史记录管理 - 最多保留 10 条"""
import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'backtest_history.json')
MAX_RECORDS = 10


def _load() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def _save(records: list) -> None:
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def save_record(record: dict) -> None:
    """保存一条回测记录，超过 MAX_RECORDS 时删除最旧的。"""
    records = _load()
    records.insert(0, record)          # 最新的放最前
    records = records[:MAX_RECORDS]    # 只保留最新 N 条
    _save(records)


def get_records() -> list:
    """返回所有历史记录（最新在前）。"""
    return _load()


def delete_record(record_id: str) -> bool:
    """按 id 删除一条记录，返回是否成功。"""
    records = _load()
    new_records = [r for r in records if r.get('id') != record_id]
    if len(new_records) == len(records):
        return False
    _save(new_records)
    return True
