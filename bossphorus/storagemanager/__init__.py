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

from .StorageManager import StorageManager
from ._FilesystemStorageManager import FilesystemStorageManager
from ._ChunkedFilesystemStorageManager import ChunkedFilesystemStorageManager
from ._RelayStorageManager import RelayStorageManager


def create(
    storage_path: str, block_size: [int, int, int], is_terminal: bool = False
) -> StorageManager:
    """
    Create a StorageManager instance.

    Depending on the arguments given, different implementations of StorageManager
    may be returned.

    Args:
        storage_path (str): Directory to the data tree.
        block_size ([int, int, int]): Amount of data to store in each file.
    Returns:
        StorageManager: A concrete instance of StorageManager.
    """
    from ._FilesystemStorageManager import FilesystemStorageManager

    return FilesystemStorageManager(storage_path, block_size, is_terminal=is_terminal)
