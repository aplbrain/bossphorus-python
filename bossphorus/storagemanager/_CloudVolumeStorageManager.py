"""
Copyright 2019 The Johns Hopkins University Applied Physics Laboratory.

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
from typing import Tuple

import os
import numpy as np

from .StorageManager import StorageManager
from .utils import file_compute, blockfile_indices


class CloudVolumeStorageManager(StorageManager):
    """
    Relay requests to a CloudVolume instance.
    """

    def __init__(
            self, storage_path: str, block_size: Tuple[int, int, int]
    ) -> None:
        """
        Create a new CloudVolumeStorageManager.

        Arguments:
            storage_path: Where to store the data tree
            block_size: How much data should go in each file
        """
        self.is_terminal = True

    def hasdata(
            self, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ):
        return self.is_terminal

    def setdata(self, data: np.array, col: str, exp: str, chan: str, res: int,
                xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]):
        """
        Upload the file.

        Arguments:
            bossURI
        """
        raise NotImplementedError("Cannot upload data.")

    def getdata(self, col: str, exp: str, chan: str, res: int,
                xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]):
        """
        Get the data from disk.

        Arguments:
            bossURI

        """
        raise NotImplementedError("Not yet implemented.")
