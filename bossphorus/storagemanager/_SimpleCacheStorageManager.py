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
from typing import List, Tuple

import numpy as np

from intern.remote.boss import BossRemote

from .StorageManager import StorageManager


class SimpleCacheStorageManager(StorageManager):
    """
    A SimpleCache is a naïve "cascade" of storage managers.

    Reads:
        Retrieves data from the first manager in `layers` that can satisfy the
            request for data

    Writes:
        Writes to ALL layers.
    """

    def __init__(self, layers: List) -> None:
        """
        Create a new SimpleCacheStorageManager.
        """
        self.layers = layers

    def hasdata(
            self, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ):
        return any([
            layer.hasdata(col, exp, chan, res, xs, ys, zs)
            for layer in self.layers
        ])

    def setdata(
            self, data: np.array, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ):
        for layer in self.layers:
            layer.setdata(data, col, exp, chan, res, xs, ys, zs)

    def getdata(
            self, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ) -> np.array:
        for layer in self.layers:
            if layer.hasdata(col, exp, chan, res, xs, ys, zs):
                return layer.getdata(col, exp, chan, res, xs, ys, zs)
        raise ValueError("Data could not be retrieved.")
