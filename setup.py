import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py3wetransfer",
    version="0.0.5",
    author="Francois Liot",
    author_email="francois@liot.org",
    description="A Python 3 wrapper to use WeTransfer API V2 upload",
    long_description="README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/fliot/py3wetransfer",
    packages=setuptools.find_packages(),
    install_requires=[
        "python-magic>=0.4",
        "requests>=2.7.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP"
    ],
)
