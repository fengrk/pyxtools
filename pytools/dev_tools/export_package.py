# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import os
import shutil
import sys
from optparse import OptionParser

from ..basic_tools import list_files, init_logger, include_patterns, remove_empty_sub_dir, compress_by_tar


def parse_args(argv=None):
    hstr = '%prog custom help string'
    parser = OptionParser(hstr, description='custom description', version='%prog 1.0')
    parser.add_option('-s', '--source', action='store', dest='source', help='source package name')
    parser.add_option('-t', '--tools', action='store', dest='tools', default="",
                      help='tool package name list, join by `,`')
    parser.add_option('-d', '--dir', action='store', dest='dir', default=".", help='working dir')
    parser.add_option('-o', '--output', action='store', dest='output', default="pylib", help='target package name')
    parser.add_option('-c', '--compress', action='store', dest='compress', default=True,
                      help='compress the target package', )
    parser.add_option('-r', '--remove', action='store', dest='remove', default=False,
                      help='remove target dir if exists', )
    return parser.parse_args(argv if argv else sys.argv)


def compress_folder(source_folder, target_file_name):
    """

    :type target_file_name: str
    :type source_folder: str
    """
    logging.info("compress {} to {}".format(source_folder, target_file_name))
    compress_by_tar(source_folder, target_file_name, absolute_dir=False)


def copy_package(source_folder: str, target_foler: str, common_package_list: list,
                 current_dir: str):
    """
    if target_foler exists, it would remove target_foler first
    """

    def check_import_package(py_content: str, package_name_list: list) -> bool:
        _error_found = False

        for _package in package_name_list:
            str_list = ["from {} ".format(_package), "from {}.".format(_package)]

            for str_pattern in str_list:
                if py_content.find(str_pattern) > -1:
                    _error_found = True
                    logging.warning("found {} in py file".format(str_pattern))

        return _error_found

    def change_import_package(py_content: str, old_pkn: str, new_pkn: str):
        _package_found = False
        str_list = ["from {} ".format(old_pkn), "from {}.".format(old_pkn)]

        for str_pattern in str_list:
            if py_content.find(str_pattern) > -1:
                _package_found = True
                py_content = py_content.replace(
                    str_pattern, str_pattern.replace(old_pkn, new_pkn, 1))

        return py_content, _package_found

    def change_common_import(_py_file: str, old_pkn: str, new_pkn: str) -> list:
        with open(_py_file, "r", encoding="utf-8") as f:
            py_content = f.read()

        common_package_using_list = []
        py_content, _ = change_import_package(py_content, old_pkn, new_pkn)
        for comm in common_package_list:
            py_content, _common_package_found = change_import_package(
                py_content, comm, "{}.{}".format(new_pkn, comm)
            )
            if _common_package_found:
                common_package_using_list.append(comm)

        package_list = [old_pkn, new_pkn]
        package_list.extend(common_package_list)

        other_package_names = [file_name for file_name in os.listdir(current_dir) if file_name not in set(package_list)]
        check_import_package(py_content, other_package_names)

        with open(_py_file, "w", encoding="utf-8") as fw:
            fw.write(py_content)

        return common_package_using_list

    def copy_package_tree(source: str, target: str):
        """
        only copy *.py in dir
        """
        shutil.copytree(source, target,
                        symlinks=False,
                        ignore=include_patterns("*.py"))

        # just remove empty folder
        remove_empty_sub_dir(target, remove_input_folder=False)

    logging.info("copy package from {} to {}".format(source_folder, target_foler))
    old_package_name = os.path.basename(source_folder)
    new_package_name = os.path.basename(target_foler)

    # copy package dir
    if os.path.exists(target_foler):
        logging.warning("remove {}".format(target_foler))
        os.remove(target_foler)

    copy_package_tree(source_folder, target_foler)

    # change root import
    py_file_list = [file_name for file_name in list_files(target_foler) if file_name.endswith(".py")]
    use_comm_pkn = list()
    for py_file in py_file_list:
        use_comm_pkn.extend(change_common_import(py_file, old_package_name, new_package_name))

    # change common package
    use_comm_pkn = set(use_comm_pkn)
    if len(use_comm_pkn) == 0:
        logging.warning("not use {}".format(common_package_list))
        return

    for common_package in use_comm_pkn:
        copy_package_tree(
            os.path.join(current_dir, common_package),
            os.path.join(target_foler, common_package))
        py_file_list = list_files(os.path.join(target_foler, common_package))
        for py_file in py_file_list:
            change_import_package(py_file, old_package_name, new_package_name)


def export_package(package_name: str, target_package_name: str, common_package_list: list,
                   is_gz=False, remove_target_dir=False, current_dir="."):
    """
    """
    # check args
    if package_name is None:
        raise ValueError("package_name cannot be null!")

    if target_package_name is None:
        raise ValueError("target_package_name cannot be null!")

    if is_gz is False and (target_package_name == package_name or target_package_name is None):
        raise ValueError("target_package_name cannot equal to package_name if is_gz=False!")

    if not os.path.exists(os.path.join(current_dir, package_name)):
        raise ValueError("sourc package [{}] not exists!".format(package_name))

    for comm_package in common_package_list:
        if not os.path.exists(os.path.join(current_dir, comm_package)):
            raise ValueError("common package [{}] not exists!".format(comm_package))

    if not os.path.exists(current_dir) or not os.path.isdir(current_dir):
        raise ValueError("current_dir[{}] is invalid!".format(current_dir))

    source_package_folder = os.path.join(current_dir, package_name)
    target_package_folder = os.path.join(current_dir, target_package_name)
    if not os.path.exists(source_package_folder):
        raise ValueError("source package not exists!")

    if target_package_folder != source_package_folder and os.path.exists(target_package_folder):
        if remove_target_dir:
            shutil.rmtree(target_package_folder)
        else:
            raise ValueError("target package folder exists!")

    # export folder to target folder
    copy_package(
        source_package_folder, target_package_folder,
        common_package_list=common_package_list,
        current_dir=current_dir,
    )

    # compress package
    if is_gz:
        compress_folder(target_package_folder, target_package_folder + ".tar.gz")


def export_package_helper():
    init_logger()
    options, args = parse_args()
    export_package(package_name=options.source,
                   target_package_name=options.output,
                   common_package_list=[comm for comm in options.tools.split(",") if len(comm) > 0],
                   is_gz=options.compress,
                   remove_target_dir=options.remove,
                   current_dir=options.dir)


__all__ = ("export_package_helper",)
