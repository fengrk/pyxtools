# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import os
import subprocess
import time


def pid_exists_by_name(name):
    if len(get_pids_by_name(name)) > 1:
        return True
    return False


def get_pids_by_name(name):
    import re
    re_pid = re.compile('\d+')

    s1 = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
    s2 = subprocess.Popen(['grep', name], stdin=s1.stdout, stdout=subprocess.PIPE)
    lines = s2.stdout.readlines()
    pids = []
    for line in lines:
        try:
            pid = re_pid.findall(line)[0]
            if pid:
                if line.find("00 grep %s" % name) == -1:
                    pids.append(pid)
                else:
                    logging.debug(line[:-1])
                    logging.debug("ignore this pid")
        except Exception as e:
            logging.error(e)
    return pids


def run_command(cmd):
    def run_bash(command, pdir='./'):
        import codecs
        try:
            if not pdir:
                file_name = str(int(time.time() % 10000)) + '.sh'
            else:
                file_name = os.path.join(pdir, str(int(time.time() % 10000)) + '.sh')
            with codecs.open(file_name, 'w', encoding='utf-8') as fw:
                fw.write('#!/bin/bash\n')
                for ccc in command:
                    fw.write(ccc + '\n')
            subprocess.Popen(['chmod', '777', file_name])
            proc = subprocess.Popen(['sh', file_name])
            # cmd 执行完成后，方执行删除指令
            proc.wait()
            os.remove(file_name)
        except Exception as e:
            logging.error(e)

    if cmd.find('gunicorn') != -1:
        os.chdir('./kiwi/server')
        s = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
        s.wait()
        os.chdir('../..')
    else:
        run_bash([cmd])


def kill_pids(pids):
    for pid in pids:
        try:
            subprocess.Popen(['kill', '-9', pid])
        except Exception as e:
            logging.error(e)


def kill_by_name(name):
    pids = get_pids_by_name(name)
    while len(pids) > 1:
        kill_pids(pids)
        time.sleep(0.1)
        pids = get_pids_by_name(name)


def create_bash(command, bash_fn):
    import codecs
    with codecs.open(bash_fn, 'w', encoding='utf-8') as fw:
        fw.write('#!/bin/bash\n')
        for cmd in command:
            fw.write(cmd + '\n')
