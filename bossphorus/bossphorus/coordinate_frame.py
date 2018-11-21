from typing import Tuple

import attr

@attr.s(frozen=True)
class CutoutCoordinateFrame:
    """Represents a specific BOSS cutout."""
    collection: str = attr.ib()
    experiment: str = attr.ib()
    channel: str = attr.ib()
    resolution: int = attr.ib()
    xs: Tuple[int, int] = attr.ib()
    ys: Tuple[int, int] = attr.ib()
    zs: Tuple[int, int] = attr.ib()
