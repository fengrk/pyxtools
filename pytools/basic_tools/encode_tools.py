# -*- coding:utf-8 -*-
from __future__ import absolute_import

import base64


def byte_to_string(byte_input: bytes, encoding="utf-8") -> str:
    """ encoding """
    return byte_input.decode(encoding)


def base64_to_string(base64_str):
    return base64.standard_b64decode(base64_str)


def string_to_base64(string):
    return base64.standard_b64encode(string)


__all__ = ("byte_to_string", "base64_to_string", "string_to_base64")
