import pathlib
import setuptools

import lodge

VERSION = "0.1.0"

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()


setuptools.setup(
    name="lodge",
    version=VERSION,
    py_modules=["lodge"],
    description="A structured logging package in Python simple to use.",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/NeowayLabs/lodge",
    author="Neoway's ML Platform team",
    license="MIT",
    keywords =["logging", "structured"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
    ],

)
