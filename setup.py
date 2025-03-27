#!/usr/bin/env python
"""
PhenoFetch - Command-line tool for downloading PhenoCam data

Copyright 2025 Samapriya Roy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import find_packages, setup

setup(
    name="phenofetch",
    version="0.1.0",
    description="Command-line tool for downloading PhenoCam data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Samapriya Roy",
    author_email="samapriya.roy@gmail.com",
    url="https://github.com/samapriya/phenofetch",
    packages=find_packages(),
    py_modules=["daily_links", "site_info", "site_stats", "size_estimate"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "aiofiles",
        "aiohttp",
        "psutil",
        "rich",
        "tqdm",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "phenofetch=phenofetch:main",
        ],
    },
)
