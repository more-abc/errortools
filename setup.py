from setuptools import setup, find_packages

setup(
    name="errortools",
    version="2.2.6",
    description="errortools - a toolset for working with Python exceptions and warnings and logging.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/more-abc/errortools",
    author="Evan Yang",
    author_email="quantbit@126.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    packages=find_packages(),
    package_data={"errortools": ["py.typed"]},
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=["namebyauthor==1.0.0"],
    entry_points={
        "console_scripts": [
            "python -m errortools = _errortools.cli:main",
            "logger = _errortools.cli:main",
        ]
    },
)
