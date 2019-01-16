# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    # license = f.read()
    licence = "Affero GPL v3"

setup(
    name='auto-mkv',
    version='0.1.0',
    description='Reencoding script',
    long_description=readme,
    url='https://github.com/adrienbricchi/auto-mkv',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

