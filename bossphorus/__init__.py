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

from typing import List

import blosc
from flask import Flask, request, Response, jsonify, make_response
import numpy as np

from .StorageManager import FilesystemStorageManager
from .config import BLOCK_SIZE, UPLOADS_PATH
from .utils import file_compute, blockfile_indices


__version__ = "0.1.0"


APP = Flask(__name__)



MANAGER = FilesystemStorageManager()


@APP.route(
    "/v1/cutout/<collection>/<experiment>/<channel>/"
    "<resolution>/<x_range>/<y_range>/<z_range>/",
    methods=["POST"]
)
def upload_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
    """
    Upload a volume.

    Uses bossURI format.
    """
    data = np.fromstring(blosc.decompress(request.data), dtype="uint8")
    xs = [int(i) for i in x_range.split(":")]
    ys = [int(i) for i in y_range.split(":")]
    zs = [int(i) for i in z_range.split(":")]
    data = data.reshape(xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0])
    data = data.transpose()
    MANAGER.setdata(data, collection, experiment, channel, resolution, zs, ys, xs)
    return make_response("", 201)


@APP.route(
    "/cutout/upload/<collection>/<experiment>/<channel>/"
    "<resolution>/<x_range>/<y_range>/<z_range>/",
    methods=["POST"]
)
def upload_cutout_json(collection, experiment, channel, resolution, x_range, y_range, z_range):
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
    "/v1/collection/<collection>/experiment/<experiment>/channel/<channel>/",
    methods=["GET"]
)
def get_channel(collection, experiment, channel):
    """
    Upload a volume.

    Uses bossURI format.
    """
    return jsonify({
        "name": channel,
        "description": "",
        "experiment": experiment,
        "default_time_sample": 0,
        "type": "image",
        "base_resolution": 0,
        "datatype": "uint8",
        "creator": "None",
        "sources": [],
        "downsample_status": "NOT_DOWNSAMPLED",
        "related": []
    })


@APP.route(
    "/v1/cutout/<collection>/<experiment>/<channel>/"
    "<resolution>/<x_range>/<y_range>/<z_range>/",
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
        data = np.ascontiguousarray(np.transpose(data))
        response = make_response(blosc.compress(data, typesize=16))
        return response
    except IOError as e:
        return Response(
            json.dumps({"message": str(e)}),
            status=404,
            mimetype="application/json"
        )


@APP.route("/")
def hello():
    """Root route."""
    return __version__


if __name__ == "__main__":
    APP.run(port=5000, debug=True)
