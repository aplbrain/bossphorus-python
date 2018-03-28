import os
from distutils.core import setup

import bossphorus

"""
git tag {VERSION}
git push --tags
python setup.py sdist upload -r pypi
"""

VERSION = bossphorus.__version__

setup(
    name="bossphorus",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="jordan.matelsky@jhuapl.edu",
    description=("Baby bossDB"),
    license="BSD",
    keywords=[
        "kindle",
        "ebook",
        "download"
    ],
    #url="https://github.com/ ... / ... /tarball/" + VERSION,
    packages=['bossphorus'],
    scripts=[
       #  'scripts/'
    ],
    classifiers=[],
    install_requires=[
        'pandas',
        'numpy'
    ],
)
