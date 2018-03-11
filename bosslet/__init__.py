#!/usr/bin/env python3

import io
import json
import os

from flask import Flask, request, Response
import numpy as np
# from intern.remote.boss import BossRemote
# from intern.resource.boss.resource import ChannelResource
# from intern.utils.parallel import block_compute
# from requests import codes, post

APP = Flask(__name__)
UPLOADS_PATH = "./uploads"


"""
https://api.theboss.io/v1/cutout/:collection/:experiment/:channel/:resolution/:x_range/:y_range/:z_range/:time_range/?iso=:iso
"""


@APP.route("/v1/cutout/<collection>/<experiment>/<channel>/<resolution>/<x_range>/<y_range>/<z_range>/", methods=["POST"])
def upload_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
    """
    Upload a volume

    """
    for _, f in request.files.items():
        memfile = io.BytesIO()
        f.save(memfile)
        data = np.fromstring(memfile.getvalue(), dtype=np.uint8)
        os.makedirs("{}/{}/{}/{}/".format(
            UPLOADS_PATH,
            collection, experiment, channel
        ), exist_ok=True)
        np.save("{}/{}/{}/{}/{}-{}-{}-{}.npy".format(
            UPLOADS_PATH,
            collection, experiment, channel,
            resolution, x_range, y_range, z_range,
        ))
    return ""


@APP.route("/v1/cutout/<collection>/<experiment>/<channel>/<resolution>/<x_range>/<y_range>/<z_range>/", methods=["GET"])
def get_cutout_xyz(collection, experiment, channel, resolution, x_range, y_range, z_range):
    """
    Upload a volume

    """
    for _, f in request.files.items():
        memfile = io.BytesIO()
        f.save(memfile)
        data = np.fromstring(memfile.getvalue(), dtype=np.uint8)
        break
    return ""


@APP.route("/")
def hello():
    """Root."""
    return "Welcome to bossDB"


if __name__ == "__main__":
    APP.run(port=5000, debug=True)
