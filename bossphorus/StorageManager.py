#!/usr/bin/env python3
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

import os
import numpy as np

from .config import BLOCK_SIZE, UPLOADS_PATH
from .utils import file_compute, blockfile_indices


class StorageManager:
    """
    Abstract class.

    StorageManagers are responsible for shutting data in and out of a storage
    mechanism, which may be a filesystem (such as FileSystemStorageManager) or
    a remote resource, such as AWS S3 or even another bossphorus.

    """

    pass


class FilesystemStorageManager(StorageManager):
    """
    File System management for volumetric data.

    Contains logic for reading and writing to local filesystem.
    """

    def __init__(
            self,
            upload_path: str = UPLOADS_PATH,
            block_size: [int, int, int] = BLOCK_SIZE
        ):
        """
        Create a new FileSystemStorageManager.

        Arguments:
            upload_path: Where to store the data tree
            block_size: How much data should go in each file
        """
        self.upload_path = upload_path
        self.block_size = block_size

    def setdata(
            self,
            data: np.array,
            col: str, exp: str, chan: str,
            res: int, xs: [int, int], ys: [int, int], zs: [int, int]
        ):
        """
        Upload the file.

        Arguments:
            bossURI
        """
        # Chunk the file into its parts
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1],
            block_size=self.block_size,
        )
        indices = blockfile_indices(
            xs, ys, zs,
            block_size=self.block_size
        )

        for f, i in zip(files, indices):
            try:
                data_partial = self.retrieve(col, exp, chan, res, f)
            except:
                data_partial = np.zeros(self.block_size, dtype="uint8")

            data_partial[
                i[0][0]:i[0][1],
                i[1][0]:i[1][1],
                i[2][0]:i[2][1],
            ] = data[
                (f[0] + i[0][0]) - xs[0]: (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0]: (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0]: (f[2] + i[2][1]) - zs[0],
            ]
            data_partial = self.store(data_partial, col, exp, chan, res, f)

    def getdata(
            self,
            col: str, exp: str, chan: str,
            res: int, xs: [int, int], ys: [int, int], zs: [int, int]
        ):
        """
        Get the data from disk.

        Arguments:
            bossURI

        """
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1],
            block_size=self.block_size,
        )
        indices = blockfile_indices(
            xs, ys, zs,
            block_size=self.block_size
        )

        payload = np.zeros((
            (xs[1] - xs[0]),
            (ys[1] - ys[0]),
            (zs[1] - zs[0])
        ), dtype="uint8")
        for f, i in zip(files, indices):
            try:
                data_partial = self.retrieve(col, exp, chan, res, f)[
                    i[0][0]:i[0][1],
                    i[1][0]:i[1][1],
                    i[2][0]:i[2][1],
                ]
            except:
                data_partial = np.zeros(self.block_size, dtype="uint8")[
                    i[0][0]:i[0][1],
                    i[1][0]:i[1][1],
                    i[2][0]:i[2][1],
                ]
            payload[
                (f[0] + i[0][0]) - xs[0]: (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0]: (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0]: (f[2] + i[2][1]) - zs[0],
            ] = data_partial

        return payload

    def store(
            self,
            data: np.array,
            col: str, exp: str, chan: str, res: int,
            b: [int, int, int]
        ):
        """
        Store a single block file.

        Arguments:
            data (np.array)
            bossURI

        """
        os.makedirs("{}/{}/{}/{}/".format(
            UPLOADS_PATH,
            col, exp, chan
        ), exist_ok=True)
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            UPLOADS_PATH,
            col, exp, chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        # print(fname)
        return np.save(fname, data)

    def retrieve(
            self,
            col: str, exp: str, chan: str, res: int,
            b: [int, int, int]
        ):
        """
        Pull a single block from disk.

        Arguments:
            bossURI

        """
        if not (
                os.path.isdir("{}/{}".format(UPLOADS_PATH, col)) and
                os.path.isdir("{}/{}/{}".format(UPLOADS_PATH, col, exp)) and
                os.path.isdir("{}/{}/{}/{}".format(
                    UPLOADS_PATH, col, exp, chan
                ))
            ):
            raise IOError("{}/{}/{} not found.".format(
                col, exp, chan
            ))
            # return np.zeros(self.block_size, dtype="uint8")
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            UPLOADS_PATH,
            col, exp, chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        return np.load(fname)
