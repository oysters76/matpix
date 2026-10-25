import numpy as np
import pytest
from PIL import Image


@pytest.fixture()
def tmp_image(tmp_path):
    path = tmp_path / "test_input.png"
    arr = np.zeros((10, 10, 3), dtype=np.uint8)
    arr[2:8, 2:8] = [255, 0, 0]
    Image.fromarray(arr).save(path)
    return path


@pytest.fixture()
def tmp_image_with_pattern(tmp_path):
    path = tmp_path / "pattern.png"
    arr = np.zeros((4, 4, 3), dtype=np.uint8)
    arr[0, 0] = [255, 0, 0]
    arr[0, 3] = [0, 255, 0]
    arr[3, 0] = [0, 0, 255]
    arr[3, 3] = [255, 255, 0]
    Image.fromarray(arr).save(path)
    return path
