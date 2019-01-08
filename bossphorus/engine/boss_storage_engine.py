import numpy as np

from intern.remote.boss import BossRemote
from intern.resource.boss import ExperimentResource, CoordinateFrameResource

from .abstract_storage_layer import AbstractStorageLayer, StorageEngine

from ..common import (
    CutoutCoordinateFrame
)


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
            self.remote.get_channel(
                coord.channel, coord.collection, coord.experiment),
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
            cf = self.remote.get_project(
                CoordinateFrameResource(exp_info.coord_frame))

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
            self.remote.get_channel(
                coord.channel, coord.collection, coord.experiment),
            coord.resolution,
            coord.xs,
            coord.ys,
            coord.zs,
            data,
        )
