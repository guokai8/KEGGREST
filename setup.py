from setuptools import setup, find_packages

setup(
    name="KEGGRESTpy",
    version="0.1.1",
    author="Kai Guo",
    author_email="guokai8@gmail.com",
    description="A Python wrapper for accessing KEGG REST API, inspired by KEGGREST in Bioconductor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/guokai8/KEGGRESTpy",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
