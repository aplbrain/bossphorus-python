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
import numpy as np

from .StorageManager import StorageManager
from .utils import file_compute, blockfile_indices


class ChunkedFileInterface(ABC):
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
        b: Tuple[int, int, int],
    ):
        ...

    @abstractmethod
    def retrieve(
        self, col: str, exp: str, chan: str, res: int, b: Tuple[int, int, int]
    ):
        ...


class NpyChunkedFileInterface(ChunkedFileInterface):
    def __init__(self, storage_path: str, block_size):
        self.storage_path = storage_path
        self.block_size = block_size
        self.format_name = "NPY"

    def __repr__(self):
        return f"<NpyChunkedFileInterface>"

    def store(
        self,
        data: np.array,
        col: str,
        exp: str,
        chan: str,
        res: int,
        b: Tuple[int, int, int],
    ):
        """
        Store a single block file.

        Arguments:
            data (np.array)
            bossURI

        """
        os.makedirs(
            "{}/{}/{}/{}/".format(self.storage_path, col, exp, chan), exist_ok=True
        )
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            self.storage_path,
            col,
            exp,
            chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        return np.save(fname, data)

    def hasfile(self, col: str, exp: str, chan: str, res: int, b: Tuple[int, int, int]) -> bool:
        if not (
            os.path.isdir("{}/{}".format(self.storage_path, col))
            and os.path.isdir("{}/{}/{}".format(self.storage_path, col, exp))
            and os.path.isdir("{}/{}/{}/{}".format(self.storage_path, col, exp, chan))
        ):
            return False
        return True


    def retrieve(
        self, col: str, exp: str, chan: str, res: int, b: Tuple[int, int, int]
    ):
        """
        Pull a single block from disk.

        Arguments:
            bossURI

        """
        if not (
            os.path.isdir("{}/{}".format(self.storage_path, col))
            and os.path.isdir("{}/{}/{}".format(self.storage_path, col, exp))
            and os.path.isdir("{}/{}/{}/{}".format(self.storage_path, col, exp, chan))
        ):
            raise IOError("{}/{}/{} not found.".format(col, exp, chan))
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            self.storage_path,
            col,
            exp,
            chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        return np.load(fname)


class ChunkedFilesystemStorageManager(StorageManager):
    """
    File System management for volumetric data.

    Contains logic for reading and writing to local filesystem.
    """

    def __init__(
        self, storage_path: str, block_size: Tuple[int, int, int], **kwargs
    ) -> None:
        """
        Create a new ChunkedFileSystemStorageManager.

        Arguments:
            storage_path: Where to store the data tree
            block_size: How much data should go in each file
            preferred_format (str: npy): file format you prefer to use on disk
        """
        self.name = "ChunkedFilesystemStorageManager"
        if "next_layer" in kwargs:
            self._next = kwargs["next_layer"]
            self.is_terminal = False
        else:
            self.is_terminal = True
        self.storage_path = storage_path
        self.block_size = block_size

        self.fs = (
            {"npy": NpyChunkedFileInterface}.get(kwargs.get("preferred_format", "npy"))
        )(self.storage_path, self.block_size)

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
        # TODO: Should know when it has data and return false even if it's
        # in terminal mode
        try:
            self.getdata(col, exp, chan, res, xs, ys, zs)
        except:
            return False
        return self.is_terminal

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
        # Chunk the file into its parts
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1], block_size=self.block_size
        )
        indices = blockfile_indices(xs, ys, zs, block_size=self.block_size)

        for f, i in zip(files, indices):
            try:
                data_partial = self.fs.retrieve(col, exp, chan, res, f)
            except Exception:
                data_partial = np.zeros(self.block_size, dtype="uint8")

            data_partial[
                i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]
            ] = data[
                (f[0] + i[0][0]) - xs[0] : (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0] : (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0] : (f[2] + i[2][1]) - zs[0],
            ]
            data_partial = self.fs.store(data_partial, col, exp, chan, res, f)

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
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1], block_size=self.block_size
        )

        indices = blockfile_indices(xs, ys, zs, block_size=self.block_size)

        payload = np.zeros(
            ((xs[1] - xs[0]), (ys[1] - ys[0]), (zs[1] - zs[0])), dtype="uint8"
        )

        for f, i in zip(files, indices):
            print(f)
            if self.fs.hasfile(col, exp, chan, res, f):
                data_partial = self.fs.retrieve(col, exp, chan, res, f)[
                    i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]
                ]
            else:
                # what to do if the file doesn't exist
                if self.is_terminal:
                    # this is a terminal; must return something, so return 0s
                    data_partial = np.zeros(self.block_size, dtype="uint8")[
                        i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]
                    ]
                else:
                    # we can cascade to a downstream:
                    # TODO: Should just fetch the data-partial instead of
                    # aborting the whole download and getting it from a
                    # remote.
                    return self._next.getdata(col, exp, chan, res, xs, ys, zs)

            payload[
                (f[0] + i[0][0]) - xs[0] : (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0] : (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0] : (f[2] + i[2][1]) - zs[0],
            ] = data_partial

        return payload

    def __str__(self):
        return f"<ChunkedFilesystemStorageManager [{str(self.fs)}]>"

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
        else:
            return [str(self), *self._next.get_stack_names()]
