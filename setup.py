#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages
import unittest


def some_function():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests")
    return test_suite


setup(
    name="cristin",
    version="0.1",
    description="Package for querying the CRISTIN APIs",
    packages=find_packages(exclude=["tests"]),
    long_description=open("README.md").read(),
    url="https://github.com/NikolaiMagnussen/ercin",
    test_suite="setup.some_function",
    author="Nikolai Magnussen",
    author_email="nikolai@magnussen.tf"
)
