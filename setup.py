# setup.py

from setuptools import setup, find_packages

setup(
    name="KEGGREST",
    version="0.1",
    description="A Python package for interacting with the KEGG REST API",
    author="Kai Guo",
    author_email="guokai8@gmail.com",
    url="https://github.com/guokai8/KEGGREST",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

