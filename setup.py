from setuptools import setup, find_packages

from errortools import __version__, __description__


def load_requirements(path: str = "requirements.txt") -> list:
    try:
        with open(path, encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return []


setup(
    name="errortools",
    version=__version__,
    description=__description__,
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/aiwonderland/errortools",
    author="Evan Yang",
    author_email="quantbit@126.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    packages=find_packages(exclude=["tests"]),
    package_data={"errortools": ["py.typed"]},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=load_requirements(),
)
