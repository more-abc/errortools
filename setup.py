import sys

from setuptools import setup, find_packages

_VERSION: str = "2.4.4"
_CLI_INFO: dict[str, list[str]] = {
    "console_scripts": [
        "python -m errortools = _errortools.cli:main",
        "logger = _errortools.cli:main",
    ]
}
_DESCRIPTION: str = (
    "errortools - a toolset for working with Python exceptions and warnings and logging."
)
_URL: str = "https://github.com/more-abc/errortools"
_AUTHOR: str = "Evan Yang"
_AUTHOR_EMAIL: str = "quantbit@126.com"
_LICENSE: str = "MIT"

if sys.version_info >= (3, 15):
    setup(
        name="errortools",
        version=_VERSION,
        description=_DESCRIPTION,
        long_description=open("README.md", encoding="utf-8").read(),
        long_description_content_type="text/markdown",
        url=_URL,
        author=_AUTHOR,
        author_email=_AUTHOR_EMAIL,
        license=_LICENSE,
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: 3.14",
            "Programming Language :: Python :: 3.15",
            "Operating System :: OS Independent",
            "Typing :: Typed",
        ],
        packages=find_packages(),
        package_data={"errortools": ["py.typed"]},
        include_package_data=True,
        python_requires=">=3.15",
        install_requires=["namebyauthor==1.0.0"],
        entry_points=_CLI_INFO,
    )
else:
    setup(
        name="errortools",
        version=_VERSION,
        description=_DESCRIPTION,
        long_description=open("README.md", encoding="utf-8").read(),
        long_description_content_type="text/markdown",
        url=_URL,
        author=_AUTHOR,
        author_email=_AUTHOR_EMAIL,
        license=_LICENSE,
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: 3.14",
            "Programming Language :: Python :: 3.15",
            "Operating System :: OS Independent",
            "Typing :: Typed",
        ],
        packages=find_packages(),
        package_data={"errortools": ["py.typed"]},
        include_package_data=True,
        python_requires=">=3.10",
        install_requires=["namebyauthor==1.0.0", "typing_extensions>=4.8.0"],
        entry_points=_CLI_INFO,
    )
