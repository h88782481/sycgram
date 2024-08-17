from loguru import logger
import sys

def init_logger():
    # 为标准错误流配置日志，适用于所有来源的日志
    logger.add(
        sys.stderr,
        format="{time} {level} {message}",
        level="INFO",
        enqueue=True
    )

    # DEBUG级别日志配置，使用大小分割来管理文件大小
    logger.add(
        './data/log/debug.app.log',
        rotation="100 MB",  # 当文件达到100MB时分割
        level="DEBUG",
        enqueue=True,
        retention="21 days"  # 保留21天的日志文件
    )

    # INFO及以上级别（排除DEBUG）的日志文件
    logger.add(
        './data/log/info.app.log',
        level="INFO",
        enqueue=True,
        retention="10 days",  # 根据需要调整保留天数
        rotation="50 MB",  # 较少的日志级别可能不需要太大的文件
    )

    # 专门用于错误和更严重级别的日志
    logger.add(
        './data/log/error.app.log',
        level="ERROR",
        enqueue=True,
        retention="30 days",  # 错误日志可能需要更长时间的保留期
        rotation="50 MB",
    )
