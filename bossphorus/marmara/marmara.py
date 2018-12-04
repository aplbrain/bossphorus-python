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

from .engine import StorageEngine


class Marmara:
    """
    An abstract class that manages multithreaded data access.

    .
    """

    def __init__(self, storage_engine: StorageEngine) -> None:
        """
        Create a new Marmara server.

        Arguments:
            storage_engine (StorageEngine): The engine to use to backend
                requests to this server.

        """
        self.storage_engine = storage_engine

    def get():
        """
        Get data from the storage engine.

        .
        """
        ...

    def has():
        """
        Check if a cutout exists in the storage engine.

        .
        """
        ...

    def put():
        """
        Put data to the storage engine.

        .
        """
        ...
