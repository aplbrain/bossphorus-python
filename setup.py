import os
from distutils.core import setup

import bosslet

"""
git tag {VERSION}
git push --tags
python setup.py sdist upload -r pypi
"""

VERSION = bosslet.__version__

setup(
    name="bosslet",
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
    packages=['bosslet'],
    scripts=[
       #  'scripts/'
    ],
    classifiers=[],
    install_requires=[
        'pandas',
        'numpy'
    ],
)
