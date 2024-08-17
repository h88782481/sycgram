import asyncio
import pickle
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger

"""
一个简单的文件存储系统.
"""
class SimpleStore:

    def __init__(self, file_name: str = './data/app.pickle', auto_flush: bool = True) -> None:
        self._lock = asyncio.Lock()
        self._file_path = Path(file_name)
        self._auto_flush = auto_flush
        self._store = self._load_store()

    async def __aenter__(self):
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._auto_flush:
            self.flush()
        self._lock.release()

    def _load_store(self) -> Dict[str, Any]:
        if self._file_path.exists():
            try:
                with self._file_path.open('rb') as file:
                    return pickle.load(file)
            except Exception as e:
                logger.error(f"加载存储失败: {e}")
            return {}
        else:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            return {}

    def get_data(self, key: str) -> Dict:
        return self._store.setdefault(key, None)
    
    def set_data(self, key: Any, value: Any):
        self._store[key] = value

    def deleter(self, key: Any) -> Optional[Any]:
        return self._store.pop(key, None)

    def flush(self):
        """更新数据并持久化到pickle文件."""
        with self._file_path.open('wb') as file:
            pickle.dump(self._store, file)
