import setuptools

import lodge


VERSION = "0.1.0"
NAME = "lodge"


setuptools.setup(
    name=NAME,
    version=VERSION,
    py_modules=["lodge"],
    description="A structured logging package in Python simple to use.",
)
