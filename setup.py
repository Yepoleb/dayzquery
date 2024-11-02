#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="dayzquery",
    version="1.2.0",
    author="Gabriel Huber",
    author_email="mail@gabrielhuber.at",
    description="Small module to decode the DayZ rules binary response.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yepoleb/dayzquery",
    py_modules=["dayzquery"],
    install_requires=["python-a2s"],
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
    python_requires=">=3.10"
)
