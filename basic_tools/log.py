# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import sys

_inited_logger = False


def get_track():
    import traceback
    return traceback.format_exc()


def get_log_file_name():
    import os
    return os.path.join(os.path.dirname(__file__), '..', '..', "all.log")


def _init_logger(logger_level=logging.INFO):
    """初始化日志配置"""

    """
    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted
    """
    logger_format = '%(asctime)s,[%(thread)d],%(name)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s'

    logging.basicConfig(stream=sys.stderr, level=logger_level, format=logger_format, datefmt='%Y-%m-%d %H:%M:%S')


def init_logger():
    global _inited_logger

    if _inited_logger is False:
        _init_logger()

        _inited_logger = True