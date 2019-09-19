#!/bin/sh

rm -rf dist/ build/
python setup.py sdist bdist_wheel
python -m twine upload dist/*
