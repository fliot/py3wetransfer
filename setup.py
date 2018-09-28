import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py3wetransfer",
    version="0.0.2",
    author="Francois Liot",
    author_email="francois@liot.org",
    description="A small wrapper to use WeTransfer API V2 upload",
    long_description="README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/fliot/py3wetransfer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
