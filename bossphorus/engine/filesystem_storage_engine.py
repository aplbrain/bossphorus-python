from typing import Tuple
import os

import numpy as np

from ..common import (
    CutoutCoordinateFrame,
    file_compute,
    blockfile_indices,
    CutoutNotFoundError
)

from .abstract_storage_layer import AbstractStorageLayer, StorageEngine


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
            raise CutoutNotFoundError(
                "Failed to load {}.".format(fname)) from e

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
                )[i[0][0]: i[0][1], i[1][0]: i[1][1], i[2][0]: i[2][1]]
            except Exception as e:
                raise CutoutNotFoundError(
                    f"Could not load coordinates {coord} from file {f}."
                ) from e
                # data_partial = np.zeros(self.block_size, dtype="uint8")[
                #     i[0][0] : i[0][1], i[1][0] : i[1][1], i[2][0] : i[2][1]
                # ]
            payload[
                (f[0] + i[0][0]) - xs[0]: (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0]: (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0]: (f[2] + i[2][1]) - zs[0],
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
                data_partial = self._retrieve(
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
                i[0][0]: i[0][1], i[1][0]: i[1][1], i[2][0]: i[2][1]
            ] = data[
                (f[0] + i[0][0]) - xs[0]: (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0]: (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0]: (f[2] + i[2][1]) - zs[0],
            ]
            data_partial = self._store(
                data_partial,
                coord.collection,
                coord.experiment,
                coord.channel,
                coord.resolution,
                f,
            )
