# Storage Managers

There are a variety of available storage managers, each with their own strengths and weaknesses. They are listed below for your reference.

*All* storage managers have `getdata`, `setdata`, and `hasdata` functions. If `hasdata` returns `True`, that is an informal promise that `getdata` with the same arguments will successfully return data without error.

## FilesystemStorageManager

Uses the filesystem as a storage mechanism for data.

Data are stored in numpy-compressed format, and are block-chunked to enable parallel data access.

## RelayStorageManager

Uses `intern` (`pip install intern`) or [`emboss`](https://github.com/aplbrain/emboss) to point to an upstream bossDB or bossphorus node.

## SimpleCacheStorageManager

Provides no smarts on its own; instead, acts as a naïve 'cascade' cache for a list of other storage managers.

For example, you could use this as a multilevel cache for a bossDB instance:

```python

SCSM = SimpleCacheStorageManager(
    layers=[
        RelayStorageManager(upstream_uri="localhost:3000"),
        RelayStorageManager(upstream_uri="my-lab-bossdb/"),
        RelayStorageManager(upstream_uri="bossdb.my-institution.edu/"),
        RelayStorageManager(upstream_uri="my-boss-instance.com/"),
    ]
)
```

...which will attempt a local cache, then a labwide cache, then an institutional cache, and finally a cloud-based bossDB, in that order.
