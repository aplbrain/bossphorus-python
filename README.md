<p align="center">
 <img align="center" alt="bossphorus" src="./logo.png" width="100" />
 <h1 align="center" fontsize="2em">b o s s p h o r u s</h1>
</p>
<p align="center">a simple volumetric datastore for dense 3D data</p>

<p align=center>
    <img src="https://img.shields.io/pypi/v/bossphorus.svg" />
    <img src="https://img.shields.io/github/last-commit/aplbrain/bossphorus.svg" />
    <img src="https://img.shields.io/badge/Extremely Rad-👌-00ddcc.svg" />
    <img src="https://img.shields.io/github/license/aplbrain/bossphorus.svg" />
</p>


> **WARNING!** *Bossphorus* is **NOT** stable and **NOT** tested. Use at your own risk, and always keep a backup copy of your data someplace safe.

## bossDB Feature Parity

For more information, see our [Features](features.md) page.

## Why use bossphorus?

*bossphorus* simplifies data-access patterns for data that do not fit into RAM. When you write a 100-gigabyte file, *bossphorus* automatically slices your dataset up to fit in bite-sized pieces.

When you request small pieces of your data for analysis, *bossphorus* intelligently serves only the parts you need, leaving the rest on disk.

## Usage

You can either run *bossphorus* using Python on your host machine, or use the provided Dockerfile to run *bossphorus* in a Docker container.

### Docker Method (Preferred)

#### 1. Build the docker image

```shell
docker build -t bossphorus .
```

#### 2. Create a directory for your filesystem to live in.

```shell
mkdir ./uploads
```

#### 3. Source the provided alias file.

This exposes a simplified wrapper to run *bossphorus* in a container.

```shell
source alias
```

#### 4. Run *bossphorus*!

```shell
bossphorus $(pwd)/uploads
```

You can run *bossphorus* in demo-mode by omitting the path to your uploads directory. **Data saved to bossphorus using this method will be destroyed when you end the bossphorus process!** Use only when testing *bossphorus* out.

### Native Method

```shell
pipenv install
mkdir ./uploads
python3 ./run.py
```

#### pip Method

```shell
pip3 install -U bossphorus
```

## Configuration

You can modify the top-level variables in `bossphorus/config.py` in order to change where bossphorus stores its data by default, and what size each file is by default.

A word of warning: While larger values of `BLOCK_SIZE` will reduce the amount of parallel threads in order to read a small file, it will also increase RAM usage per read. 256<sup>3</sup> is probably a good default, unless you have a very good reason to change it.

---

### Why bossphorus instead of other volumetric services?

That's a great question! *bossphorus* is certainly not the most performant, nor is it the most secure. And it's not versioned or distributed. If you're looking for a volumetric datastore, I would recommend looking below at the _Alternatives_ section for some really well-engineered systems.

The primary advantage of *bossphorus* is that it uses an identical API to that of [bossDB](https://bossdb.org) — and so if you anticipate your data growing from a few gigabytes now to a few terabytes later, you can get used to the bossDB ecosystem ([intern](https://https://github.com/jhuapl-boss/intern), [ingest](https://github.com/jhuapl-boss/ingest-client), and [many more tools](https://github.com/aplbrain/)) _now_, and then invest in real bossDB architecture later on with a seamless transition.

## Why is it called bossphorus?

*bossphorus* borrows its indexing pattern from _[bossDB](https://bossdb.org)_, a cloud-native database that can store way more data than *bossphorus* ever could. If your day-to-day routine includes multiple terabytes of volumetric data, [bossDB](https://bossdb.org) may be for you.

## Alternatives

| Project | Description |
|---------|-------------|
| [bossDB](https://bossdb.org) | Petabyte-scale, Cloud-Native Volumetric Database |
| [DVID](https://github.com/janelia-flyem/dvid) | Distributed, Versioned, Image-oriented Dataservice


## Contributing

### Updating the Documentation

When you make any changes to outward-facing APIs or services, you must update the documentation. To do so, run the following:

```shell
cd website/                                # enter the docusaurus dir
yarn                                       # install dependencies
GIT_USER=XXXX yarn run publish-gh-pages    # build and upload the documentation
```

-----

<p align="center"><small>Made with ♥ at <a href="http://www.jhuapl.edu/"><img alt="JHU APL" align="center" src="./website/static/img/apl-logo.png" height="23px"></a></small></p>
