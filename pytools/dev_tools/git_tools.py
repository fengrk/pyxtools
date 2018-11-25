# -*- coding:utf-8 -*-
from __future__ import absolute_import

import os
from subprocess import check_output


def git_list_status_file() -> list:
    """ list all file showed in `git status -s` """
    raw_lines = check_output(["git", "status", "-s"]).decode("utf-8").split("\n")

    def _get_file_name(_line: str) -> str:
        blank_index = _line.find(" ")
        if blank_index > -1:
            return _line[blank_index:]
        return ""

    lines = [_get_file_name(clear_line) for clear_line in [line.strip("\r").strip() for line in raw_lines]]
    return [file_name for file_name in [line.strip() for line in lines] if len(file_name) > 0]


def is_git_repo_log_dir(log_dir: str) -> bool:
    return os.path.isdir(log_dir) and \
           os.path.exists(os.path.join(log_dir, "index")) and \
           os.path.exists(os.path.join(log_dir, "HEAD"))


def find_git_log_dir(path: str) -> (str, str):
    while True:
        if not os.path.exists(path) or not os.path.isdir(path):
            raise ValueError("fail to find git log dir")

        git_log = os.path.join(path, ".git")
        if os.path.exists(git_log):
            if is_git_repo_log_dir(git_log):
                return path, git_log
        else:
            with open(git_log, "r", encoding="utf-8") as f:
                for line in f:
                    if line.find("gitdir:") > -1:
                        relative_path = line[line.find("gitdir:"):].strip("\n").strip("\r").strip()
                        real_git_log = os.path.join(path, relative_path)
                        if is_git_repo_log_dir(real_git_log):
                            return path, real_git_log

        path = os.path.join(path, "..")
