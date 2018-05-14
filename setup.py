import os
from distutils.core import setup

import bossphorus

"""
git tag {VERSION}
git push --tags
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
"""

VERSION = bossphorus.__version__

setup(
    name="bossphorus",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="jordan.matelsky@jhuapl.edu",
    description=("Baby bossDB"),
    license="Apache 2.0",
    keywords="bossDB neuroscience volumetric datastore database",
    url="https://github.com/aplbran/bossphorus/tarball/" + VERSION,
    packages=['bossphorus'],
    scripts=[
       #  'scripts/'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'pandas',
        'numpy'
    ],
)
