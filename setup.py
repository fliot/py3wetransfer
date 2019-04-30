import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py3-wetransfer",
    version="1.0.0",
    author="Sander Huijsen",
    author_email="sander.huijsen@gmail.com",
    maintainer="Sander Huijsen",
    maintainer_email="sander.huijsen@gmail.com",
    description="A Python 3 wrapper to use WeTransfer API V2 transfer and board",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sandyman/py3-wetransfer",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.7.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP"
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
