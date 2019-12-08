#!/usr/bin/python3
# -*-coding:utf8 -*

# auto-mkv
# Copyright (C) 2019-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

