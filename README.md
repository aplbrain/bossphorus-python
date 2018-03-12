<p align="center">
<h1 align="center"> b o s s l e t</h1>
<img align="center" width="200" src="./logo.png" />
<p>a simple volumetric datastore for dense 3D data</p>
</p>

## Usage

You can either run *bosslet* using Python on your host machine, or use the provided Dockerfile to run *bosslet* in a Docker container.

### Docker Method (Preferred)

#### 1. Build the docker image

```shell
docker built -t bosslet .
```

#### 2. Create a directory for your filesystem to live in.

```shell
mkdir ./uploads
```

#### 3. Source the provided alias file.

This exposes a simplified wrapper to run *bosslet* in a container.

```shell
source alias
```

#### 4. Run *bosslet*!

```shell
bosslet $(pwd)/uploads
```

You can run *bosslet* in demo-mode by omitting the path to your uploads directory. **Data saved to bosslet using this method will be destroyed when you end the bosslet process!** Use only when testing *bosslet* out.

### Native Method

```shell
pipenv install
mkdir ./uploads
python3 ./run.py
```

## Configuration

You can modify the top-level variables in `bosslet/config.py` in order to change where bosslet stores its data by default, and what size each file is by default.

A word of warning: While larger values of `BLOCK_SIZE` will reduce the amount of parallel threads in order to read a small file, it will also increase RAM usage per read. 256<sup>3</sup> is probably a good default, unless you have a very good reason to change it.

---

## Why use bosslet?

*bosslet* simplifies data-access patterns for data that do not fit into RAM. When you write a 100-gigabyte file, *bosslet* automatically slices your dataset up to fit in bite-sized pieces.

When you request small pieces of your data for analysis, *bosslet* intelligently serves only the parts you need, leaving the rest on disk.

### Why bosslet instead of other volumetric services?

That's a great question! *bosslet* is certainly not the most performant, nor is it the most secure. And it's not versioned or distributed. If you're looking for a volumetric datastore, I would recommend looking below at the _Alternatives_ section for some really well-engineered systems.

The primary advantage of *bosslet* is that it uses an identical API to that of [bossDB](https://bossdb.org) — and so if you anticipate your data growing from a few gigabytes now to a few terabytes later, you can get used to the bossDB ecosystem ([intern](https://https://github.com/jhuapl-boss/intern), [ingest](https://github.com/jhuapl-boss/ingest-client), and [many more tools](https://github.com/aplbrain/)) _now_, and then invest in real bossDB architecture later on with a seamless transition.

## Why is it called bosslet?

*bosslet* borrows its indexing pattern from _[bossDB](https://bossdb.org)_, a cloud-native database that can store way more data than *bosslet* ever could. If your day-to-day routine includes multiple terabytes of volumetric data, [bossDB](https://bossdb.org) may be for you.

## Alternatives

| Project | Description |
|---------|-------------|
| [bossDB](https://bossdb.org) | Petabyte-scale, Cloud-Native Volumetric Database |
| [DVID](https://github.com/janelia-flyem/dvid) | Distributed, Versioned, Image-oriented Dataservice
