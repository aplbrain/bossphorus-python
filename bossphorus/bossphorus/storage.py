import numpy as np
from typing_extensions import Protocol

from .coordinate_frame import CutoutCoordinateFrame

class StorageProxy(Protocol):
    """
    A StorageProxy proxies the storage and retrieval of data to some concrete storage backend.

    The StorageProxy protocol does not make any assumptions about how or where
    data are stored.
    """

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
