# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import math

import hashlib
import uuid


def create_guid():
    return str(uuid.uuid1()).lower()


def create_fake_random_string(length: int) -> str:
    assert length > 0

    md5_list = [get_md5(create_guid().encode("utf-8")) for _ in range(math.ceil(length / 30) + 1)]

    return "".join(md5_list)[:length]


def get_md5(string) -> str:
    """
    use in python3.6:
    get_md5("x".encode("utf-8"))
    """
    hash_md5 = hashlib.md5(string)
    return hash_md5.hexdigest()


def get_md5_for_file(file_or_filename):
    if isinstance(file_or_filename, str):
        hash_md5 = hashlib.md5()
        with open(file_or_filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file_or_filename.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()
