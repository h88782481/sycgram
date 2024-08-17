from configparser import ConfigParser
from loguru import logger
import os

class BotConfigParser:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.getcwd(), "data/config.ini")
        self._config_path = config_path
        self.config = ConfigParser()
        self._is_loaded = False  # 标记配置文件是否成功加载

    def config_read(self):
        if self._is_loaded:  # 如果配置已经加载，直接返回
            return
        try:
            self.config.read(self._config_path, encoding="utf-8")
            self._is_loaded = True
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            logger.complete()
            self._is_loaded = False

    def get_config(self):
        if not self._is_loaded:  # 仅当配置未加载时，尝试读取配置
            self.config_read()
        if self._is_loaded:
            return self.config
        else:
            logger.error("配置未成功加载.")
            logger.complete()
            return None
