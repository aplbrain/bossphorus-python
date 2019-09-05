---
layout: home
---

![](img/boss2x2.png)

# bossphorus

Bossphorus is a volumetric datastore and cache layer that emulates the [bossDB](https://bossdb.org) HTTP API.

This means that you can use bossphorus as a multi-tier cache for very large 3D or 4D datasets that live in the cloud — or you can use it to serve data from a server's filesystem.

## Why use bossphorus?

### Bossphorus is a simple datastore.

Bossphorus is a good solution if you have large volumetric data (i.e. bigger than RAM) and you want to access your data from multiple client machines.

### Bossphorus is a stackable cache.

Bossphorus can act as a cache for other volumetric databases. You can use Bossphorus to bring commonly-accessed data on-prem, or you can stack multiple Bossphorus instances to speed up data access for you and your collaborators. This also means that you can reduce your cloud-access costs for frequent requests by storing them in an on-prem Bossphorus deploy.

## Getting Started

You can set up a ready-to-run bossphorus deployment using the single-line docker deploy command:

```shell
docker run -p 5050:5050 aplbrain/bossphorus
```

For more configurations and details, see [Getting Started](start).
