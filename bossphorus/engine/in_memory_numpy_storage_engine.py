import numpy as np

from .abstract_storage_layer import AbstractStorageLayer, StorageEngine

from ..common import CutoutCoordinateFrame


class InMemoryNumpyStorageEngine(AbstractStorageLayer):
    """
    A StorageEngine that keeps all data in-memory.

    Note: This is not a good option for real use-cases, but may be good for
    writing tests or prototyping small data.
    """

    def __init__(self, data: np.ndarray, next_layer: StorageEngine = None) -> None:
        super().__init__(next_layer)
        self.data = data

    def _get(self, coord: CutoutCoordinateFrame) -> np.ndarray:
        """
        Get data from the cutout.

        .
        """
        return self.data[
            coord.xs[0] : coord.xs[1],
            coord.ys[0] : coord.ys[1],
            coord.zs[0] : coord.zs[1],
        ]

    def _has(self, coord: CutoutCoordinateFrame) -> bool:
        """
        Check if the cutout can be returned.

        Returns true if the requested cutout is smaller than the size of the
        provisioned numpy array.
        """
        return (
            (coord.xs[0] <= self.data.shape[0] and coord.xs[1] <= self.data.shape[0])
            and (
                coord.ys[0] <= self.data.shape[1] and coord.ys[1] <= self.data.shape[1]
            )
            and (
                coord.zs[0] <= self.data.shape[2] and coord.zs[1] <= self.data.shape[2]
            )
        )

    def _put(self, coord: CutoutCoordinateFrame, data: np.ndarray) -> None:
        """
        Broadcast a numpy array to the storage backend.

        .
        """
        self.data[
            coord.xs[0] : coord.xs[1],
            coord.ys[0] : coord.ys[1],
            coord.zs[0] : coord.zs[1],
        ] = data
