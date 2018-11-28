import numpy as np
import pytest

from bossphorus.common import CutoutCoordinateFrame
from bossphorus.marmara.engine import InMemoryNumpyStorageEngine

@pytest.fixture
def in_memory_engine():
    return InMemoryNumpyStorageEngine(np.zeros((10, 10, 10)))

@pytest.fixture
def frame():
    return CutoutCoordinateFrame(
        collection="foo",
        experiment="bar",
        channel="baz",
        resolution=0,
        xs=[1, 3],
        ys=[5, 8],
        zs=[2, 10],
    )

def test_in_memory_numpy_storage_engine_get(in_memory_engine, frame):
    expected = np.zeros((2, 3, 8))
    actual = in_memory_engine.get(frame)
    assert np.array_equal(actual, expected)

def test_in_memory_numpy_storage_engine_has(in_memory_engine, frame):
    assert in_memory_engine.has(frame)

def test_in_memory_numpy_storage_engine_put(in_memory_engine, frame):
    data = np.ones((2, 3, 8))
    in_memory_engine.put(frame, data)

    actual = in_memory_engine.get(frame)
    assert np.array_equal(actual, data)

def test_invalid_shape_in_memory_numpy_storage_engine(frame):
    # should fail on 2D source data
    se = InMemoryNumpyStorageEngine(np.zeros((10, 10)))

    with pytest.raises(IndexError):
        se.get(frame)

    with pytest.raises(IndexError):
        se.has(frame)

    with pytest.raises(IndexError):
        se.put(frame, np.ones((10, 10)))

def test_shape_mismatch_in_memory_numpy_storage_engine_put(in_memory_engine, frame):
    data = np.zeros((4, 4, 4))
    with pytest.raises(ValueError):
        in_memory_engine.put(frame, data)
