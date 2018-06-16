from ._FilesystemStorageManager import FilesystemStorageManager
from .StorageManager import StorageManager


def create(storage_path: str, block_size: [int, int, int]) -> StorageManager:
    return FilesystemStorageManager(storage_path, block_size)