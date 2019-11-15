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
from typing import Tuple, List
from abc import ABC, abstractmethod

import os
import h5py
import numpy as np

from .StorageManager import StorageManager


class FileInterface(ABC):
    """
    A filesystem manager that handles transit from numpy in-memory to a
    static format on disk.
    """

    format_name = "None"

    @abstractmethod
    def store(
        self,
        data: np.array,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        ...

    @abstractmethod
    def retrieve(
        self,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        ...


class H5FileInterface(FileInterface):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.format_name = "h5"

    def __repr__(self):
        return f"<H5FileInterface>"

    def store(
        self,
        data: np.array,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        os.makedirs(f"{self.storage_path}/{col}/{exp}/{chan}", exist_ok=True)
        fname = f"{self.storage_path}/{col}/{exp}/{chan}/{res}.h5"
        if os.path.exists(fname):
            # Open in readwrite
            with h5py.File(fname, "r+") as fh:
                contents = fh["data"]
                contents.resize(
                    (
                        max(contents.shape[0], xs[1]),
                        max(contents.shape[1], ys[1]),
                        max(contents.shape[2], zs[1]),
                    )
                )
                contents[xs[0] : xs[1], ys[0] : ys[1], zs[0] : zs[1]] = data
                fh["data"][...] = contents
        else:
            # Create a new file in write-only:
            with h5py.File(fname, "w") as fh:
                d = fh.create_dataset(
                    "data",
                    (xs[1], ys[1], zs[1]),
                    dtype=data.dtype,
                    chunks=(128, 128, 128),
                )
                m = fh.create_dataset(
                    "mask", (xs[1], ys[1], zs[1]), dtype="b", chunks=(128, 128, 128)
                )
                m[:] = False
                d[xs[0] : xs[1], ys[0] : ys[1], zs[0] : zs[1]] = data
                m[xs[0] : xs[1], ys[0] : ys[1], zs[0] : zs[1]] = True

    def retrieve(
        self,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        fname = f"{self.storage_path}/{col}/{exp}/{chan}/{res}.h5"
        return h5py.File(fname, "r")["data"][
            xs[0] : xs[1], ys[0] : ys[1], zs[0] : zs[1]
        ]

    def hasdata(
        self,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        fname = f"{self.storage_path}/{col}/{exp}/{chan}/{res}.h5"
        if not os.path.isfile(fname):
            return False
        return h5py.File(fname, "r")["mask"][
            xs[0] : xs[1], ys[0] : ys[1], zs[0] : zs[1]
        ].all()


class FilesystemStorageManager(StorageManager):
    """
    File System management for volumetric data.

    Contains logic for reading and writing to local filesystem.
    """

    def __init__(
        self, storage_path: str, block_size: Tuple[int, int, int], **kwargs
    ) -> None:
        """
        Create a new FileSystemStorageManager.

        Arguments:
            storage_path: Where to store the data tree
            block_size: How much data should go in each file
            preferred_format (str: npy): file format you prefer to use on disk
        """
        self.name = "FilesystemStorageManager"
        if "next_layer" in kwargs:
            self._next = kwargs["next_layer"]
            self.is_terminal = False
        else:
            self.is_terminal = True
        self.storage_path = storage_path
        self.block_size = block_size
        self._cache = kwargs.get("cache", True)

        self.fs = ({"h5": H5FileInterface}.get(kwargs.get("preferred_format", "h5")))(
            self.storage_path
        )

    def hasdata(
        self,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        if self.is_terminal:
            return True

        return self.fs.hasdata(col, exp, chan, res, xs, ys, zs)

    def setdata(
        self,
        data: np.array,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        """
        Upload the file.

        Arguments:
            bossURI
        """
        self.fs.store(data, col, exp, chan, res, xs, ys, zs)

    def getdata(
        self,
        col: str,
        exp: str,
        chan: str,
        res: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        """
        Get the data from disk.

        Arguments:
            bossURI

        """
        if self.hasdata(col, exp, chan, res, xs, ys, zs):
            return self.fs.retrieve(col, exp, chan, res, xs, ys, zs)
        if self.is_terminal:
            raise IndexError("Cannot find data at: ", (col, exp, chan, res, xs, ys, zs))
        data = self._next.getdata(col, exp, chan, res, xs, ys, zs)
        if self._cache:
            self.setdata(data, col, exp, chan, res, xs, ys, zs)
        return data

    def __str__(self):
        return f"<FilesystemStorageManager [{str(self.fs)}]>"

    def get_stack_names(self):
        """
        Get a list of the names of the storage managers that back this one.

        Arguments:
            None

        Returns:
            List[str]

        """
        if self.is_terminal:
            return [str(self)]
        return [str(self), *self._next.get_stack_names()]
