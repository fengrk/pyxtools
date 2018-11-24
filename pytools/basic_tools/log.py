# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import sys

_inited_logger_args = None


def _clear_logger_handlers(_logger):
    while _logger.handlers:
        _handler = _logger.handlers[0]
        _logger.removeHandler(_handler)


def _logger_config_is_same(used_args, to_use_args) -> bool:
    if used_args[0] != to_use_args[0] or used_args[2] != to_use_args[2]:
        return False

    if isinstance(used_args[1], list) and isinstance(to_use_args[1], list):
        used_sorted_args = list(used_args[1])
        used_sorted_args.sort()
        to_use_sorted_args = list(to_use_args[1])
        to_use_sorted_args.sort()
        return "<<>>".join(to_use_sorted_args) == "<<>>".join(used_sorted_args)

    return used_args[1] == to_use_args[1]


def global_init_logger(logger_level=logging.INFO, log_file: str = None, reset_logger_name_list: list = None):
    global _inited_logger_args

    if _inited_logger_args is not None and _logger_config_is_same(_inited_logger_args,
                                                                  (log_file, reset_logger_name_list, logger_level)):
        logging.warning("init logger run before!")
        return

    # formatter
    _default_formatter = logging.Formatter("%(asctime)s %(filename)s - %(name)s - %(levelname)s - %(message)s", None)

    # reset other logger
    if reset_logger_name_list is not None:
        for logger_name in reset_logger_name_list:
            _clear_logger_handlers(logging.getLogger(logger_name))

    # reset root logger
    root_logger = logging.getLogger()
    _clear_logger_handlers(root_logger)

    # console handler
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setFormatter(_default_formatter)
    root_logger.addHandler(_console_handler)

    # file handler
    if log_file is not None:
        _file_handler = logging.FileHandler(log_file)
        _file_handler.setFormatter(_default_formatter)
        root_logger.addHandler(_file_handler)

    root_logger.setLevel(logger_level)

    if reset_logger_name_list is None:
        _inited_logger = (log_file, None, logger_level)
    else:
        _inited_logger = (log_file, list(reset_logger_name_list), logger_level)


__all__ = ("global_init_logger",)
