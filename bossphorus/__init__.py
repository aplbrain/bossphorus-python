from . import common
from . import marmara
from . import storage
from . import version

__version__ = version.__version__

class Bossphorus:

    def __init__(self, proxy: storage.StorageProxy) -> None:
        self.proxy = proxy


def create_app(bossphorus: Bossphorus):
    # Importing here so as to not pollute the bossphorus package namespace.
    import blosc
    from flask import Flask, make_response, request
    import numpy as np

    app = Flask(__name__)

    @app.route(
        "/v1/cutout/<collection>/<experiment>/<channel>/"
        "<resolution>/<x_range>/<y_range>/<z_range>/",
        methods=["POST"],
    )
    def upload_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
        """
        Upload a cutout.
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
        coord = coordinate_frame.CutoutCoordinateFrame(
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
        methods=["GET"]
    )
    def get_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
        """
        Download a cutout.
        """
        xs = [int(i) for i in x_range.split(":")]
        ys = [int(i) for i in y_range.split(":")]
        zs = [int(i) for i in z_range.split(":")]

        coord = coordinate_frame.CutoutCoordinateFrame(
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

    return app
