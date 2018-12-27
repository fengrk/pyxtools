# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

ver_dic = {}
version_file = open("version.py")
try:
    version_file_contents = version_file.read()
finally:
    version_file.close()

exec(compile(version_file_contents, "version.py", 'exec'), ver_dic)

setup(name="pyxtools",
      version=ver_dic["VERSION_TEXT"],
      description="simple tool for Python3.6",
      long_description=open("README.rst", "r").read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Other Audience',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ],

      install_requires=[
          "requests",
          "chardet",
          "aiohttp>=3.1.3",
          "faiss-prebuilt",
      ],

      author="frkhit",
      url="https://github.com/frkhit/pyxtools",
      author_email="frkhit@gmail.com",
      license="MIT",
      packages=find_packages())
