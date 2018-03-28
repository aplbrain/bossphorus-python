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

from .config import BLOCK_SIZE


def file_compute(
        x_start: int, x_stop: int,
        y_start: int, y_stop: int,
        z_start: int, z_stop: int,
        block_size: [int, int, int] = BLOCK_SIZE
    ):
    """
    Compute the (possibly extant) files that would hold this volume.

    Which files do we need to pull for this volume?

    Arguments:
        q_start, q_stop: Bounds along Q dimension
        block_size: The block-size stored in each file
    """
    # x

    x_block_origins = [
        b
        for b in range(0, x_stop + block_size[0], block_size[0])
        if b > (x_start - block_size[0]) and b < x_stop
    ]
    y_block_origins = [
        b
        for b in range(0, y_stop + block_size[1], block_size[1])
        if b > (y_start - block_size[1]) and b < y_stop
    ]
    z_block_origins = [
        b
        for b in range(0, z_stop + block_size[2], block_size[2])
        if b > (z_start - block_size[2]) and b < z_stop
    ]

    files = []
    for x in x_block_origins:
        for y in y_block_origins:
            for z in z_block_origins:
                files.append((x, y, z))
    return files


def block_compute(
        x_start: int, x_stop: int,
        y_start: int, y_stop: int,
        z_start: int, z_stop: int,
        block_size: [int, int, int] = (256, 256, 256)):
    """
    Compute the block-aligned delimiters for this volume.

    What are the block-aligned indices for this volume?

    """
    x_block_origins = [
        b
        for b in range(0, x_stop + block_size[0], block_size[0])
        if b > (x_start - block_size[0]) and b < x_stop
    ]
    x_block_origins[0] = max(x_block_origins[0], x_start)
    x_block_origins[-1] = min(x_block_origins[-1], x_stop)

    y_block_origins = [
        b
        for b in range(0, y_stop + block_size[1], block_size[1])
        if b > (y_start - block_size[1]) and b < y_stop
    ]
    y_block_origins[0] = max(y_block_origins[0], y_start)
    y_block_origins[-1] = min(y_block_origins[-1], y_stop)

    z_block_origins = [
        b
        for b in range(0, z_stop + block_size[2], block_size[2])
        if b > (z_start - block_size[2]) and b < z_stop
    ]
    z_block_origins[0] = max(z_block_origins[0], z_start)
    z_block_origins[-1] = min(z_block_origins[-1], z_stop)

    files = []
    for x in x_block_origins:
        for y in y_block_origins:
            for z in z_block_origins:
                files.append((
                    (x, min(x_stop, x+block_size[0])),
                    (y, min(y_stop, y+block_size[1])),
                    (z, min(z_stop, z+block_size[2]))
                ))
    return files


def blockfile_indices(
        xs: [int, int],
        ys: [int, int],
        zs: [int, int],
        block_size: [int, int, int] = BLOCK_SIZE
    ):
    """
    Return the indices PER BLOCK for each file required.

    Returns the indices of the offset PER BLOCK of each file that is
    required in order to construct the final volume.

    For instance, in 1D:

    Blocksize is 100, origin is 0.

    Request of (10, 50)  returns                       (10, 50)
    Request of (10, 150) returns             (10, 100), (0, 50)
    Request of (10, 250) returns (10, 100), (0, 100), (100, 50)
    """
    blocks = block_compute(
        xs[0], xs[1], ys[0], ys[1], zs[0], zs[1],
        block_size
    )
    files = file_compute(
        xs[0], xs[1], ys[0], ys[1], zs[0], zs[1],
        block_size
    )

    inds = []
    for b, f in zip(blocks, files):
        inds.append([
            (b[0][0] - f[0], b[0][1] - f[0]),
            (b[1][0] - f[1], b[1][1] - f[1]),
            (b[2][0] - f[2], b[2][1] - f[2])
        ])

    return inds
