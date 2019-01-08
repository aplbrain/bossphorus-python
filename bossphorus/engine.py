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
from typing import Tuple
from typing_extensions import Protocol
import os

import numpy as np

from intern.remote.boss import BossRemote
from intern.resource.boss import ExperimentResource, CoordinateFrameResource

from .common import (
    CutoutCoordinateFrame,
    file_compute,
    block_compute,
    blockfile_indices,
)


class CutoutNotFoundError(Exception):
    """Raise when a cutout cannot be found on the associated engine."""


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


class FilesystemStorageEngine(AbstractStorageLayer):
    def __init__(
        self,
        root_path: str,
        block_size: Tuple[int, int, int] = (256, 256, 256),
        next_layer: StorageEngine = None,
    ) -> None:
        super().__init__(next_layer)
        self.root_path = root_path
        self.block_size = block_size

    def _retrieve(
        self, col: str, exp: str, chan: str, res: int, b: Tuple[int, int, int]
    ):
        """
        Pull a single block from disk.
        Arguments:
            bossURI
        """
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            self.root_path,
            col,
            exp,
            chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        try:
            return np.load(fname)
        except Exception as e:
            raise CutoutNotFoundError("Failed to load {}.".format(fname)) from e

    def _store(
        self,
        data: np.array,
        col: str,
        exp: str,
        chan: str,
        res: int,
        b: Tuple[int, int, int],
    ):
        """
        Store a single block file.
        Arguments:
            data (np.array)
            bossURI
        """
        os.makedirs(
            "{}/{}/{}/{}/".format(self.root_path, col, exp, chan), exist_ok=True
        )
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            self.root_path,
            col,
            exp,
            chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        return np.save(fname, data)

    def _get(self, coord: CutoutCoordinateFrame) -> np.ndarray:
        xs = coord.xs
        ys = coord.ys
        zs = coord.zs

        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1], block_size=self.block_size
        )
        indices = blockfile_indices(xs, ys, zs, block_size=self.block_size)

        payload = np.zeros(
            ((xs[1] - xs[0]), (ys[1] - ys[0]), (zs[1] - zs[0])), dtype="uint8"
        )  # TODO: guess datatype instead of hardcoding
        for f, i in zip(files, indices):
            try:
                data_partial = self._retrieve(
                    coord.collection,
                    coord.experiment,
                    coord.channel,
                    coord.resolution,
                    f,
                )[i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]]
            except Exception as e:
                raise CutoutNotFoundError(
                    f"Could not load coordinates {coord} from file {f}."
                ) from e
                # data_partial = np.zeros(self.block_size, dtype="uint8")[
                #     i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]
                # ]
            payload[
                (f[0] + i[0][0]) - xs[0] : (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0] : (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0] : (f[2] + i[2][1]) - zs[0],
            ] = data_partial

        return payload.T

    def _has(self, coord: CutoutCoordinateFrame) -> bool:
        files = file_compute(
            coord.xs[0],
            coord.xs[1],
            coord.ys[0],
            coord.ys[1],
            coord.zs[0],
            coord.zs[1],
            block_size=self.block_size,
        )
        for fname in files:
            if not os.path.isfile(fname):
                return False
        return True

    def _put(self, coord: CutoutCoordinateFrame, data: np.ndarray) -> None:
        """
        Upload the file.
        Arguments:
            bossURI
        """
        xs = coord.xs
        ys = coord.ys
        zs = coord.zs
        # Chunk the file into its parts
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1], block_size=self.block_size
        )
        indices = blockfile_indices(xs, ys, zs, block_size=self.block_size)

        for f, i in zip(files, indices):
            try:
                data_partial = self.retrieve(
                    coord.collection,
                    coord.experiment,
                    coord.channel,
                    coord.resolution,
                    f,
                )
            except Exception:
                # TODO: infer datatype to create empty array
                data_partial = np.zeros(self.block_size, dtype="uint8")

            data_partial[
                i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]
            ] = data[
                (f[0] + i[0][0]) - xs[0] : (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0] : (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0] : (f[2] + i[2][1]) - zs[0],
            ]
            data_partial = self._store(
                data_partial,
                coord.collection,
                coord.experiment,
                coord.channel,
                coord.resolution,
                f,
            )


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


class BossStorageEngine(AbstractStorageLayer):
    """
    A StorageEngine that proxies a bossDB instance.

    .
    """

    def __init__(self, remote: BossRemote, next_layer: StorageEngine = None) -> None:
        """
        Construct a new Boss storage engine.

        Uses a bossDB-like API to get and store data.

        Arguments:
            remote
            next_layer

        """
        super().__init__(next_layer)
        self.remote = remote

    def _get(self, coord: CutoutCoordinateFrame) -> np.ndarray:
        return self.remote.get_cutout(
            self.remote.get_channel(coord.channel, coord.collection, coord.experiment),
            coord.resolution,
            coord.xs,
            coord.ys,
            coord.zs,
        )

    def _has(self, coord: CutoutCoordinateFrame) -> bool:
        # does col/ex/chan exist?
        try:
            _ = self.remote.get_channel(
                coord.channel, coord.collection, coord.experiment
            )
        except Exception:
            return False

        # does coordframe exist?
        try:
            exp_info = self.remote.get_project(
                ExperimentResource(coord.experiment, coord.collection)
            )
            cf = self.remote.get_project(CoordinateFrameResource(exp_info.coord_frame))

            # Does coordinate frame contain data bounds?
            return (
                (coord.xs[0] >= cf.x_start and coord.xs[1] <= cf.x_stop)
                and (coord.ys[0] >= cf.y_start and coord.ys[1] <= cf.y_stop)
                and (coord.ys[0] >= cf.y_start and coord.ys[1] <= cf.y_stop)
            )
        except Exception:
            return False

    def _put(self, coord: CutoutCoordinateFrame, data: np.ndarray) -> None:
        self.remote.post_cutout(
            self.remote.get_channel(coord.channel, coord.collection, coord.experiment),
            coord.resolution,
            coord.xs,
            coord.ys,
            coord.zs,
            data,
        )
