"""
Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages

"""
git tag {VERSION}
git push --tags
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
"""

VERSION = "0.2.0"

setup(
    name="bossphorus",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="jordan.matelsky@jhuapl.edu",
    description="Baby bossDB",
    license="Apache 2.0",
    keywords="bossDB neuroscience volumetric datastore database",
    url="https://github.com/aplbran/bossphorus/tarball/" + VERSION,
    packages=find_packages(),
    install_requires=[
        "blosc",
        "flask",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "bossphorus = bossphorus.__main__:main",
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ]
)
