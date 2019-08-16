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

import numpy as np

from intern.remote.boss import BossRemote

from .StorageManager import StorageManager


class RelayStorageManager(StorageManager):
    """

    """

    def __init__(self, **kwargs):
        """
        Create a new RelayStorageManager.

        Arguments:

            block_size: How much data should go in each file
        """
        self.block_size = kwargs.get("block_size", (256, 256, 16))

        if "next_layer" in kwargs:
            self._next = kwargs["next_layer"]
            self.is_terminal = False
        else:
            self.is_terminal = True

        if "boss_remote" in kwargs:
            self.boss_remote = kwargs["boss_remote"]
        elif "upstream_uri" in kwargs:
            self.boss_remote = BossRemote({
                "host": kwargs["upstream_uri"],
                "protocol": kwargs.get("protocol", "http"),
                "token": kwargs.get("token", "no-token")
            })

    def hasdata(
            self, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ):
        has_data = self.boss_remote.get_channel(f"bossdb://{col}/{exp}/{chan}")
        if has_data:
            return True

        if not self.is_terminal:
            return self._next.hasdata(col, exp, chan, res, xs, ys, zs)
        return False

    def setdata(
            self, data: np.array, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ):
        return self.boss_remote.create_cutout(
            self.boss_remote.get_channel(chan, col, exp), res, xs, ys, zs, data
        )

    def getdata(
            self, col: str, exp: str, chan: str, res: int,
            xs: Tuple[int, int], ys: Tuple[int, int], zs: Tuple[int, int]
    ) -> np.array:
        return self.boss_remote.get_cutout(
            self.boss_remote.get_channel(chan, col, exp), res, xs, ys, zs
        )

    def __repr__(self):
        return f"<RelayStorageManager [{str(self.boss_remote)}]>"

    def get_stack_names(self):
        if self.is_terminal:
            return [str(self)]
        else:
            return [
                str(self),
                *self._next.get_stack_names()
            ]
