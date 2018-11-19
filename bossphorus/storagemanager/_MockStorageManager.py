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
from typing import Tuple

import os
import numpy as np

from .StorageManager import StorageManager
from .utils import file_compute, blockfile_indices


class MockStorageManager(StorageManager):
    """

    """

    def __init__(self, is_terminal=True):
        """
        Create a new mocker.

        """
        self.is_terminal = is_terminal

    def hasdata(
            self, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ):
        return exp != "nodata"

    def setdata(self, data: np.array, col: str, exp: str, chan: str, res: int,
                xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]):
        """
        """
        raise NotImplementedError("You cannot upload data to this storage manager.")

    def getdata(self, col: str, exp: str, chan: str, res: int,
                xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]):
        """
        Get random data from disk.

        Arguments:
            bossURI

        """
        try:
            value = int(chan)
            payload = np.ones((xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0]), dtype='uint8') * value
        except ValueError:
            payload = np.random.randint(0, 255, (xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0]), dtype='uint8')
        return payload

