#!/usr/bin/env python3

# std
from distutils.core import setup

# noinspection PyUnresolvedReferences
import setuptools  # see below (1)
from pathlib import Path

# (1) see https://stackoverflow.com/questions/8295644/
# Without this import, install_requires won't work.


keywords = [
    "zettelkasten"
]

description = (
    "Helper scripts for markdown based Zettelkasten."
)

this_dir = Path(__file__).resolve().parent

packages = setuptools.find_packages()

with (this_dir / "README.rst").open() as fh:
    long_description = fh.read()

with (this_dir / "verzettler" / "version.txt").open() as vf:
    version = vf.read()

with (this_dir / "requirements.txt").open() as rf:
    requirements = [
        req.strip()
        for req in rf.readlines()
        if req.strip() and not req.startswith("#")
    ]


setup(
    name="verzettler",
    version=version,
    packages=packages,
    install_requires=requirements,
    url="https://github.com/klieret/verzettler",
    project_urls={
        "Bug Tracker": "https://github.com/klieret/verzettler/issues",
        "Source Code": "https://github.com/klieret/verzettler/",
    },
    include_package_data=True,
    keywords=keywords,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    entry_points={
        "console_scripts": [
            "zk_add_id = verzettler.bin.zk_add_id:cli",
            "zk_find_id = verzettler.bin.zk_find_id:cli",
            "zk_get_id = verzettler.bin.zk_get_id:cli",
            "zk_list_tags = verzettler.bin.zk_list_tags:cli",
            "zk_modify_tags = verzettler.bin.zk_modify_tags:cli",
            "zk_open = verzettler.bin.zk_open:cli",
            "zk_stats = verzettler.bin.zk_stats:cli",
            "zk_touch = verzettler.bin.zk_touch:cli",
            "zk_transform = verzettler.bin.zk_transform:cli",
            "zk_web = verzettler.bin.zk_web:cli",
            "zk_convert = verzettler.bin.zk_convert:cli",
            "zk_server = verzettler.bin.zk_server:main",
        ]
    }
)
