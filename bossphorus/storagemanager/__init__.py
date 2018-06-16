from .StorageManager import StorageManager

def create(storage_path: str, block_size: [int, int, int]) -> StorageManager:
    from ._FilesystemStorageManager import FilesystemStorageManager

    return FilesystemStorageManager(storage_path, block_size)
