from setuptools import setup, find_packages

setup(
    author="Andrew Holguin",
    description="",
    name="cimis",
    version="0.0.1",
    packages=find_packages(include=["cimis", "cimis.*"]),
    install_requires=[
        "pandas>=1.0"
    ],
    python_requires=">=3.5"
)
