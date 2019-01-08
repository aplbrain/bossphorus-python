from abc import ABC, abstractmethod
from typing_extensions import Protocol

import numpy as np

from ..common import CutoutCoordinateFrame, CutoutNotFoundError


class StorageEngine(Protocol):
    """
    A StorageEngine handles the storage and retrieval of data.

    The StorageEngine protocol does not make any assumptions about how or where
    data are stored.
    """

    # pylint: disable=unused-argument
    def get(self, coord: CutoutCoordinateFrame) -> np.ndarray:
        """
        Retrieve data from a given `CutoutCoordinateFrame`.

        Arguments:
            coord (marmara.CutoutCoordinateFrame): The cutout to request

        Returns:
            np.ndarray: Data in XYZ (?) format

        Raises:
            IndexError: If the cutout cannot be made from the Resource.

        """
        ...

    # pylint: disable=unused-argument
    def has(self, coord: CutoutCoordinateFrame) -> bool:
        """
        Determine whether the storage engine has the _full_ cutout or not.

        For example, if a user requests [0..10] and the storage engine only has
        the data [1..10], this will return false.

        Arguments:
            coord (marmara.CutoutCoordinateFrame): The cutout to request

        Returns:
            bool: True if the StorageEngine can provide the full cutout.

        """
        ...

    def put(self, coord: CutoutCoordinateFrame, data: np.ndarray) -> None:
        """
        Post data to the storage engine.

        Some StorageEngines may not implement `StorageEngine#put` (such as in
        the case of data mirrors).

        Arguments:
            coord (marmara.CutoutCoordinateFrame): The cutout to request.
            data (np.ndarray): The XYZ-order 3D data to post.

        Returns:
            None

        Raises:
            IndexError: If data.shape does not match the size of coord.
            ValueError: If another issue is encountered during posting.

        """
        ...


class AbstractStorageLayer(ABC, StorageEngine):
    """
    An abstract layer that gets and sets data from a cache parfait.

    .
    """

    def __init__(self, next_layer: StorageEngine = None) -> None:
        """
        Construct a new AbstractStorageLayer.

        Given a next layer to check in case of failure.
        """
        self.next_layer = next_layer

    def get(self, coord: CutoutCoordinateFrame) -> np.ndarray:
        """
        Retrieve data from a given `CutoutCoordinateFrame`.

        Arguments:
            coord (marmara.CutoutCoordinateFrame): The cutout to request

        Returns:
            np.ndarray: Data in XYZ (?) format

        Raises:
            IndexError: If the cutout cannot be made from the Resource.

        """
        try:
            return self._get(coord)
        except CutoutNotFoundError as e:
            if self.next_layer:
                return self.next_layer.get(coord)
            raise e

    @abstractmethod
    def _get(self, coord: CutoutCoordinateFrame) -> np.ndarray:
        ...

    def has(self, coord: CutoutCoordinateFrame) -> bool:
        """
        Determine whether the storage engine has the _full_ cutout or not.

        For example, if a user requests [0..10] and the storage engine only has
        the data [1..10], this will return false.

        Arguments:
            coord (marmara.CutoutCoordinateFrame): The cutout to request

        Returns:
            bool: True if the StorageEngine can provide the full cutout.

        """
        if not self._has(coord):
            if self.next_layer:
                return self.next_layer.has(coord)
            return False
        return True

    @abstractmethod
    def _has(self, coord: CutoutCoordinateFrame) -> bool:
        ...

    def put(self, coord: CutoutCoordinateFrame, data: np.ndarray) -> None:
        """
        Post data to the storage engine.

        Some StorageEngines may not implement `StorageEngine#put` (such as in
        the case of data mirrors).

        Arguments:
            coord (marmara.CutoutCoordinateFrame): The cutout to request.
            data (np.ndarray): The XYZ-order 3D data to post.

        Returns:
            None

        Raises:
            IndexError: If data.shape does not match the size of coord.
            ValueError: If another issue is encountered during posting.

        """
        try:
            return self._put(coord, data)
        except CutoutNotFoundError as e:
            if self.next_layer:
                return self.next_layer.put(coord, data)
            raise e

    @abstractmethod
    def _put(self, coord: CutoutCoordinateFrame, data: np.ndarray) -> None:
        ...
