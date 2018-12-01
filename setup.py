#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : setup.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


from setuptools import setup

long_description = """
fregate help you to install kubernetes with all fancy services
"""

setup(
    name='fregate',
    version='1.0',
    description='Multi nodes - Kubernetes Cluster CLI',
    scripts=[
        "bin/fregate"
    ],
    author='Antoine CHINY',
    author_email='antoine.chiny@inria.fr',
    url='https://gitlab.dotfile.eu/tonychg/fregate',
    packages=[
        "lib/fregate",
        "lib/fregate.commands",
        "lib/fregate.services",
        "lib/fregate.commons",
    ],
    install_requires=[
        "pyyaml",
        "jinja2"
    ],
    long_description=long_description,
    python_requires='>=3.4',
    classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "License :: Other/Proprietary License",
      "Programming Language :: Python :: 3",
    ],
)
