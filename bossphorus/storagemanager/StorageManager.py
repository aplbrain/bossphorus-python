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

from abc import ABC, abstractmethod

import numpy as np


class StorageManager(ABC):
    """
    Abstract Class for volumetric data management.

    StorageManagers are responsible for shutting data in and out of a storage
    mechanism, which may be a filesystem or a remote resource, such as AWS S3
    or even another bossphorus.
    """

    @abstractmethod
    def getdata(self, col: str, exp: str, chan: str,
                res: int, xs: [int, int], ys: [int, int], zs: [int, int]):
        pass

    @abstractmethod
    def setdata(self, data: np.array, col: str, exp: str, chan: str,
                res: int, xs: [int, int], ys: [int, int], zs: [int, int]):
        pass
