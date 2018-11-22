# -*- coding:utf-8 -*-
import subprocess


def is_aliyun():
    import os
    return os.path.exists('/usr/local/cloudmonitor/')


def get_my_ip_list():
    if is_aliyun():
        info = get_aliyun_address()
    else:
        info = get_campany_computer_address()

    ip_list = list(info.values())
    ip_list.append("127.0.0.1")
    return list(set(ip_list))


def get_os():
    import platform
    os_name = platform.system().lower()
    if os_name.find('window') != -1:
        return "windows"
    if os_name.find("linux") != -1:
        return "linux"
    return "mac"


def get_aliyun_address():
    out_string = get_string_of_command(["ifconfig"])
    import re
    re_address = re.compile(r'(?<=inet addr:)[\d\.]{3,20}?(?= )')
    all_address = re_address.findall(out_string)
    return {i: ip for i, ip in enumerate(all_address)}


def get_windows_address():
    out_string = get_string_of_command(["ipconfig"])
    import re
    ip_re = re.compile(r'192.168.10.\d{1,3}')
    all_ip = ip_re.findall(out_string)
    for ip in all_ip:
        if ip.find("255") == -1:
            return {"eth0": ip}
    raise Exception("cannot find ip!")


def get_campany_computer_address():
    if get_os() == "windows":
        return get_windows_address()
    else:
        return get_other_address()


def get_other_address():
    out_string = get_string_of_command(["ifconfig"])
    import re
    ip_re = re.compile(r'192.168.10.\d{1,3}')
    all_ip = ip_re.findall(out_string)
    for ip in all_ip:
        if ip.find("255") == -1:
            return {"eth0": ip}
    raise Exception("cannot find ip!")


def get_string_of_command(list_command):
    s1 = subprocess.Popen(list_command, stdout=subprocess.PIPE)
    return s1.stdout.read()


def get_string_of_pipe_command(list_command, *list_commands):
    if list_commands:
        s = subprocess.Popen(list_command, stdout=subprocess.PIPE)
        for command in list_commands:
            s_next = subprocess.Popen(command, stdin=s.stdout, stdout=subprocess.PIPE)
            s = s_next
        return s.stdout.read()
    else:
        return get_string_of_command(list_command)
