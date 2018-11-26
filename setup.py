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
    author='Antoine CHINY',
    author_email='antoine.chiny@inria.fr',
    url='https://gitlab.dotfile.eu/tonychg/fregate',
    packages=[
        "fregate.commands",
        "fregate.services",
        "fregate.commons",
    ],
    install_requires=[
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
