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

from . import common
from . import marmara
from . import storage
from . import version

__version__ = version.__version__


class Bossphorus:
    """A class that handles scheduling calls to a storage proxy."""
    def __init__(self, proxy: storage.StorageProxy) -> None:
        self.proxy = proxy


def create_app(bossphorus: Bossphorus, name: str = None):
    """
    Create a new API app.

    Arguments:
        bossphorus
        name

    Returns:
        Flask.App

    """
    # Importing here so as to not pollute the bossphorus package namespace.
    import blosc
    from flask import Flask, make_response, request, jsonify
    import numpy as np

    app = Flask(name if name else __name__)

    @app.route(
        "/v1/cutout/<collection>/<experiment>/<channel>/"
        "<resolution>/<x_range>/<y_range>/<z_range>/",
        methods=["POST"],
    )
    # pylint: disable=unused-variable
    def upload_cutout_xyz(
            collection, experiment, channel, resolution, x_range, y_range, z_range
    ):
        """
        Upload a cutout.

        .
        """
        # Decompress data from the blosc volume sent over the wire
        data = np.fromstring(blosc.decompress(request.data), dtype="uint8")
        # Reshape the data to be the correct size/shape/dimensions.
        # Here, data are in XYZ order.
        xs = [int(i) for i in x_range.split(":")]
        ys = [int(i) for i in y_range.split(":")]
        zs = [int(i) for i in z_range.split(":")]
        data = data.reshape(xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0])
        data = data.transpose()

        # Send the decompressed data to the backend storage engine
        coord = common.CutoutCoordinateFrame(
            collection=collection,
            experiment=experiment,
            channel=channel,
            resolution=resolution,
            xs=xs,
            ys=ys,
            zs=zs,
        )
        bossphorus.proxy.put(coord, data)
        return make_response("", 201)

    @app.route(
        "/v1/cutout/<collection>/<experiment>/<channel>/"
        "<resolution>/<x_range>/<y_range>/<z_range>/",
        methods=["GET"],
    )
    # pylint: disable=unused-variable
    def get_cutout_xyz(
            collection, experiment, channel, resolution, x_range, y_range, z_range
    ):
        """
        Download a cutout.

        .
        """
        xs = [int(i) for i in x_range.split(":")]
        ys = [int(i) for i in y_range.split(":")]
        zs = [int(i) for i in z_range.split(":")]

        coord = common.CutoutCoordinateFrame(
            collection=collection,
            experiment=experiment,
            channel=channel,
            resolution=resolution,
            xs=xs,
            ys=ys,
            zs=zs,
        )
        data = bossphorus.proxy.get(coord)
        data = np.ascontiguousarray(data)
        response = make_response(blosc.compress(data, typesize=16))
        return response

    @app.route(
        "/v1/collection/<collection>/experiment/<experiment>/channel/<channel>/",
        methods=["GET"],
    )
    # pylint: disable=unused-variable
    def get_channel(collection, experiment, channel):
        """
        Get a channel metadata.

        Use bossURI format.

        Need to look up metadata instead of mocking.
        """
        return jsonify(
            {
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
                "related": [],
            }
        )

    @app.route("/v1/collection/<collection>/experiment/<experiment>/", methods=["GET"])
    # pylint: disable=unused-variable
    def get_experiment(collection, experiment):
        """
        Get experiment metadata.

        Uses bossURI format.

        Look up metadata?
        """
        return jsonify(
            {
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
                "related": [],
            }
        )

    @app.route("/v1/coord/<coordframe>/", methods=["GET"])
    # pylint: disable=unused-variable
    def get_coordinate_frame(coordframe):
        """
        Uses bossURI format.

        TODO
        """
        return jsonify({"name": coordframe, "base_resolution": 0, "creator": "None"})

    return app
