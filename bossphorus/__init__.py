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

import blosc
from flask import Flask, request, Response, jsonify, make_response, render_template
import numpy as np

from . import storagemanager
from . import version

__version__ = version.__version__


def create_app(mgr: storagemanager.StorageManager = None):
    """
    Create a Bossphorus server app.
    """
    app = Flask(__name__, os.path.realpath(__file__))
    if mgr:
        manager = mgr
    else:
        manager = storagemanager.create("./uploads", (256, 256, 256))

    @app.route(
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
        manager.setdata(data, collection, experiment,
                        channel, resolution, zs, ys, xs)
        return make_response("", 201)

    @app.route(
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
            manager.setdata(data, collection, experiment,
                            channel, resolution, xs, ys, zs)
        return ""

    @app.route(
        "/v1/collection/<collection>/experiment/<experiment>/channel/<channel>/",
        methods=["GET"]
    )
    def get_channel(collection, experiment, channel):
        """
        Uses bossURI format.
        """
        return jsonify({
            "name": channel,
            "description": "",
            "experiment": experiment,
            "collection": collection,
            "default_time_sample": 0,
            "type": "image",
            "base_resolution": 0,
            "datatype": "uint8",
            "creator": "None",
            "sources": [],
            "downsample_status": "NOT_DOWNSAMPLED",
            "related": []
        })

    @app.route(
        "/v1/collection/<collection>/experiment/<experiment>/",
        methods=["GET"]
    )
    def get_experiment(collection, experiment):
        """

        Uses bossURI format.
        """
        return jsonify({
            "name": experiment,
            "collection": collection,
            "coord_frame": "NoneSpecified",  # TODO
            "description": "",
            "type": "image",
            "base_resolution": 0,
            "datatype": "uint8",
            "creator": "None",
            "sources": [],
            "downsample_status": "NOT_DOWNSAMPLED",
            "related": []
        })

    @app.route(
        "/v1/coord/<coordframe>/",
        methods=["GET"]
    )
    def get_coordinate_frame(coordframe):
        """

        Uses bossURI format.
        """
        return jsonify({
            "name": coordframe,
            "base_resolution": 0,
            "creator": "None",
        })

    @app.route(
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
            data = manager.getdata(
                collection, experiment, channel, resolution, xs, ys, zs)
            data = np.ascontiguousarray(np.transpose(data))
            response = make_response(blosc.compress(data, typesize=16))
            return response
        except IOError as e:
            return Response(
                json.dumps({"message": str(e)}),
                status=404,
                mimetype="application/json"
            )

    @app.route("/")
    def home():
        return render_template("home.html", **{
            "version": __version__,
            "cache_stack":
                [*manager.get_stack_names()]

        })

    return app
