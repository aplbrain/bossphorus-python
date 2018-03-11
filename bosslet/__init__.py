#!/usr/bin/env python3

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

import io
import json
import os

from typing import List

from flask import Flask, request, Response, jsonify
import numpy as np


APP = Flask(__name__)


UPLOADS_PATH: str = "./uploads"
BLOCK_SIZE: [int, int, int] = (256, 256, 256)


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


class StorageManager:
    """
    Abstract class.

    StorageManagers are responsible for shutting data in and out of a storage
    mechanism, which may be a filesystem (such as FileSystemStorageManager) or
    a remote resource, such as AWS S3 or even another bosslet.

    """

    pass


class FilesystemStorageManager(StorageManager):
    """
    File System management for volumetric data.

    Contains logic for reading and writing to local filesystem.
    """

    def __init__(
            self,
            upload_path: str = UPLOADS_PATH,
            block_size: [int, int, int] = BLOCK_SIZE
        ):
        """
        Create a new FileSystemStorageManager.

        Arguments:
            upload_path: Where to store the data tree
            block_size: How much data should go in each file
        """
        self.upload_path = upload_path
        self.block_size = block_size

    def setdata(
            self,
            data: np.array,
            col: str, exp: str, chan: str,
            res: int, xs: [int, int], ys: [int, int], zs: [int, int]
        ):
        """
        Upload the file.

        Arguments:
            bossURI
        """
        # Chunk the file into its parts
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1],
            block_size=self.block_size,
        )
        indices = blockfile_indices(
            xs, ys, zs,
            block_size=self.block_size
        )

        for f, i in zip(files, indices):
            try:
                data_partial = self.retrieve(col, exp, chan, res, f)
            except:
                data_partial = np.zeros(self.block_size, dtype="uint8")

            data_partial[
                i[0][0]:i[0][1],
                i[1][0]:i[1][1],
                i[2][0]:i[2][1],
            ] = data[
                (f[0] + i[0][0]) - xs[0]: (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0]: (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0]: (f[2] + i[2][1]) - zs[0],
            ]
            data_partial = self.store(data_partial, col, exp, chan, res, f)

    def getdata(
            self,
            col: str, exp: str, chan: str,
            res: int, xs: [int, int], ys: [int, int], zs: [int, int]
        ):
        """
        Get the data from disk.

        Arguments:
            bossURI

        """
        files = file_compute(
            xs[0], xs[1], ys[0], ys[1], zs[0], zs[1],
            block_size=self.block_size,
        )
        indices = blockfile_indices(
            xs, ys, zs,
            block_size=self.block_size
        )

        payload = np.zeros((
            (xs[1] - xs[0]),
            (ys[1] - ys[0]),
            (zs[1] - zs[0])
        ), dtype="uint8")
        for f, i in zip(files, indices):
            try:
                data_partial = self.retrieve(col, exp, chan, res, f)[
                    i[0][0]:i[0][1],
                    i[1][0]:i[1][1],
                    i[2][0]:i[2][1],
                ]
            except:
                data_partial = np.zeros(self.block_size, dtype="uint8")[
                    i[0][0]:i[0][1],
                    i[1][0]:i[1][1],
                    i[2][0]:i[2][1],
                ]
            payload[
                (f[0] + i[0][0]) - xs[0]: (f[0] + i[0][1]) - xs[0],
                (f[1] + i[1][0]) - ys[0]: (f[1] + i[1][1]) - ys[0],
                (f[2] + i[2][0]) - zs[0]: (f[2] + i[2][1]) - zs[0],
            ] = data_partial

        return payload

    def store(
            self,
            data: np.array,
            col: str, exp: str, chan: str, res: int,
            b: [int, int, int]
        ):
        """
        Store a single block file.

        Arguments:
            data (np.array)
            bossURI

        """
        os.makedirs("{}/{}/{}/{}/".format(
            UPLOADS_PATH,
            col, exp, chan
        ), exist_ok=True)
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            UPLOADS_PATH,
            col, exp, chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        # print(fname)
        return np.save(fname, data)

    def retrieve(
            self,
            col: str, exp: str, chan: str, res: int,
            b: [int, int, int]
        ):
        """
        Pull a single block from disk.

        Arguments:
            bossURI

        """
        if not (
                os.path.isdir("{}/{}".format(UPLOADS_PATH, col)) and
                os.path.isdir("{}/{}/{}".format(UPLOADS_PATH, col, exp)) and
                os.path.isdir("{}/{}/{}/{}".format(
                    UPLOADS_PATH, col, exp, chan
                ))
            ):
            raise IOError("{}/{}/{} not found.".format(
                col, exp, chan
            ))
            # return np.zeros(self.block_size, dtype="uint8")
        fname = "{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            UPLOADS_PATH,
            col, exp, chan,
            res,
            (b[0], b[0] + self.block_size[0]),
            (b[1], b[1] + self.block_size[1]),
            (b[2], b[2] + self.block_size[2]),
        )
        return np.load(fname)



MANAGER = FilesystemStorageManager()


@APP.route(
    "/v1/cutout/<collection>/<experiment>/<channel>/<resolution>/<x_range>/<y_range>/<z_range>/",
    methods=["POST"]
)
def upload_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
    """
    Upload a volume.

    Uses bossURI format.
    """
    for _, f in request.files.items():
        memfile = io.BytesIO()
        f.save(memfile)
        data = np.fromstring(memfile.getvalue(), dtype="uint8")
        xs = [int(i) for i in x_range.split(":")]
        ys = [int(i) for i in y_range.split(":")]
        zs = [int(i) for i in z_range.split(":")]
        data = data.reshape(xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0])
        MANAGER.setdata(data, collection, experiment, channel, resolution, xs, ys, zs)
    return ""


@APP.route(
    "/v1/cutout/<collection>/<experiment>/<channel>/<resolution>/<x_range>/<y_range>/<z_range>/",
    methods=["GET"]
)
def get_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
    """
    Download a volume.

    Returns 404 if the bossURI is not found.
    """
    xs = [int(i) for i in x_range.split(":")]
    ys = [int(i) for i in y_range.split(":")]
    zs = [int(i) for i in z_range.split(":")]
    try:
        data = MANAGER.getdata(collection, experiment, channel, resolution, xs, ys, zs)
        res = {}
        res["dtype"] = str(data.dtype)
        res["data"] = data.tolist()
        return jsonify(res)
    except IOError as e:
        return Response(
            json.dumps({"message": str(e)}),
            status=404,
            mimetype="application/json"
        )


@APP.route("/")
def hello():
    """Root."""
    return "Welcome to bossDB"


if __name__ == "__main__":
    APP.run(port=5000, debug=True)
