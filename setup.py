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
