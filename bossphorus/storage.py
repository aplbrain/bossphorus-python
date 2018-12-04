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

import numpy as np
from typing_extensions import Protocol

from .common import CutoutCoordinateFrame

from .marmara.engine import StorageEngine


class StorageProxy(Protocol):
    """
    A StorageProxy proxies the storage and retrieval of data to some concrete storage backend.

    The StorageProxy protocol does not make any assumptions about how or where
    data are stored.
    """

    # pylint: disable=unused-argument
    def get(self, coord: CutoutCoordinateFrame) -> np.array:
        """
        Retrieve a cutout from the proxied storage backend at the given `CutoutCoordinateFrame`.

        Arguments:
            coord (bossphorus.CutoutCoordinateFrame): The cutout to request.

        Returns:
            nd.array: Data in XYZ format.

        Raises:
            IndexError: If the cutout cannot be made from the Resource.

        """
        ...

    # pylint: disable=unused-argument
    def has(self, coord: CutoutCoordinateFrame) -> bool:
        """
        Determine whether the proxied storage backend has the _full_ cutout or not.

        For example, if a user requests [0..10] and the storage engine only has
        the data [1..10], this will return False.

        Arguments:
            coord (bossphorus.CutoutCoordinateFrame): The cutout to request.

        Returns:
            bool: True if the `StorageProxy` can provide the full cutout.

        """
        ...

    # pylint: disable=unused-argument
    def put(self, coord: CutoutCoordinateFrame, data: np.array) -> None:
        """
        Store data in the the proxied storage backend.

        Some storage backends may prohibit put operations, such as in
        the case of data mirrors.

        Arguments:
            coord (bossphorus.CutoutCoordinateFrame): The cutout to request.
            data (np.array): The XYZ-order 3D data to store.

        Returns:
            None

        Raises:
            IndexError: If data.shape does not match the size of coord.
            ValueError: If another issue is encountered during storing.

        """
        ...


class InProcessStorageProxy(StorageProxy):
    """
    A StorageProxy that lives in memory.

    Does not persist data across executions.
    """

    def __init__(self, engine: StorageEngine) -> None:
        """
        Create a new same-process StorageProxy with a custom StorageEngine.

        .
        """
        self._engine = engine

    def get(self, coord: CutoutCoordinateFrame) -> np.array:
        """
        Retrieve a cutout from the proxied storage backend at the given `CutoutCoordinateFrame`.

        Arguments:
            coord (bossphorus.CutoutCoordinateFrame): The cutout to request.

        Returns:
            nd.array: Data in XYZ format.

        Raises:
            IndexError: If the cutout cannot be made from the Resource.

        """
        return self._engine.get(coord)

    def has(self, coord: CutoutCoordinateFrame) -> bool:
        """
        Determine whether the proxied storage backend has the _full_ cutout or not.

        For example, if a user requests [0..10] and the storage engine only has
        the data [1..10], this will return False.

        Arguments:
            coord (bossphorus.CutoutCoordinateFrame): The cutout to request.

        Returns:
            bool: True if the `StorageProxy` can provide the full cutout.

        """
        return self._engine.has(coord)

    def put(self, coord: CutoutCoordinateFrame, data: np.array) -> None:
        """
        Store data in the the proxied storage backend.

        Some storage backends may prohibit put operations, such as in
        the case of data mirrors.

        Arguments:
            coord (bossphorus.CutoutCoordinateFrame): The cutout to request.
            data (np.array): The XYZ-order 3D data to store.

        Returns:
            None

        Raises:
            IndexError: If data.shape does not match the size of coord.
            ValueError: If another issue is encountered during storing.

        """
        return self._engine.put(coord, data)
