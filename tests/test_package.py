import re


def test_version_format():
    import matpix

    assert re.match(r"^\d+\.\d+\.\d+$", matpix.__version__)


def test_all_exports():
    import matpix

    assert "cartesian_to_pixel" in matpix.__all__
    assert "pixel_to_cartesian" in matpix.__all__
    assert "mat_transform_png" in matpix.__all__


def test_public_api_importable():
    from matpix import cartesian_to_pixel, mat_transform_png, pixel_to_cartesian

    assert callable(cartesian_to_pixel)
    assert callable(pixel_to_cartesian)
    assert callable(mat_transform_png)
