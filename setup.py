from setuptools import setup, find_packages
from secmail.config import VERSION

name = "1secMail"
author = "qvco"
author_email = "nikola.desuga@gmail.com"
description = "Create and receive email in only 1 second! 📧 An API wrapper for www.1secmail.com written in Python."
long_description_content_type = "text/markdown"
license = "MIT"
url = "https://github.com/qvco/1secMail-Python"

keywords = [
    "1secmail",
    "onesecmail",
    "tempmail",
    "disposable",
    "temporary",
    "email",
    "api",
    "wrapper",
    "library",
]

install_requires = ["httpx>=0.17.1"]

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=name,
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    version=VERSION,
    description=description,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    license=license,
    url=url,
    download_url=url,
    keywords=keywords,
    install_requires=install_requires,
    classifiers=classifiers,
    packages=find_packages(),
)
