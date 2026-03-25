#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup
from pathlib import Path

from errortools import __version__, __description__

HERE = Path(__file__).parent

README = (HERE / "README.md").read_text(encoding="utf-8")


setup(
    name="errortools",
    version=__version__,

    description=__description__,
    long_description=README,
    long_description_content_type="markdown",

    # url="https://github.com/aiwonderland/errortools",
    author="Evan Yang",
    author_email="quantbit@126.com",

    license="MIT",
    # Not yet
)