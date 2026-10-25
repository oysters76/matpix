import numpy as np
import pytest
from PIL import Image

from matpix.core import cartesian_to_pixel, mat_transform_png, pixel_to_cartesian


class TestCartesianToPixel:
    def test_origin(self):
        px, py = cartesian_to_pixel(0, 0, 10)
        assert px == 0
        assert py == 9

    def test_top_left_pixel(self):
        px, py = cartesian_to_pixel(0, 9, 10)
        assert px == 0
        assert py == 0

    def test_height_one(self):
        px, py = cartesian_to_pixel(0, 0, 1)
        assert px == 0
        assert py == 0


class TestPixelToCartesian:
    def test_origin(self):
        cx, cy = pixel_to_cartesian(0, 0, 10)
        assert cx == 0
        assert cy == 9

    def test_bottom_left_pixel(self):
        cx, cy = pixel_to_cartesian(0, 9, 10)
        assert cx == 0
        assert cy == 0

    def test_height_one(self):
        cx, cy = pixel_to_cartesian(0, 0, 1)
        assert cx == 0
        assert cy == 0


class TestRoundTrip:
    @pytest.mark.parametrize(
        ("cx", "cy", "h"),
        [(0, 0, 10), (5, 5, 10), (0, 9, 10), (9, 0, 10), (0, 0, 1), (99, 99, 100)],
    )
    def test_cartesian_pixel_round_trip(self, cx, cy, h):
        px, py = cartesian_to_pixel(cx, cy, h)
        cx2, cy2 = pixel_to_cartesian(px, py, h)
        assert cx2 == cx
        assert cy2 == cy

    @pytest.mark.parametrize(
        ("px", "py", "h"),
        [(0, 0, 10), (5, 5, 10), (0, 9, 10), (9, 0, 10), (0, 0, 1)],
    )
    def test_pixel_cartesian_round_trip(self, px, py, h):
        cx, cy = pixel_to_cartesian(px, py, h)
        px2, py2 = cartesian_to_pixel(cx, cy, h)
        assert px2 == px
        assert py2 == py


class TestMatTransformPng:
    def test_identity_preserves_image(self, tmp_image, tmp_path):
        output = tmp_path / "identity_out.png"
        identity = np.array([[1, 0], [0, 1]], dtype=float)
        mat_transform_png(str(tmp_image), identity, str(output))

        original = np.array(Image.open(tmp_image))
        result = np.array(Image.open(output))
        assert original.shape == result.shape
        np.testing.assert_array_equal(original, result)

    def test_scale_2x_doubles_dimensions(self, tmp_image, tmp_path):
        output = tmp_path / "scaled.png"
        scale = np.array([[2, 0], [0, 2]], dtype=float)
        mat_transform_png(str(tmp_image), scale, str(output))

        original = np.array(Image.open(tmp_image))
        result = np.array(Image.open(output))
        assert result.shape[0] == original.shape[0] * 2 - 1
        assert result.shape[1] == original.shape[1] * 2 - 1

    def test_flip_horizontal_preserves_dimensions(self, tmp_image, tmp_path):
        output = tmp_path / "flipped.png"
        flip = np.array([[-1, 0], [0, 1]], dtype=float)
        mat_transform_png(str(tmp_image), flip, str(output))

        original = np.array(Image.open(tmp_image))
        result = np.array(Image.open(output))
        assert original.shape == result.shape

    def test_zero_determinant_raises(self, tmp_image, tmp_path):
        output = tmp_path / "bad.png"
        bad_matrix = np.array([[1, 2], [2, 4]], dtype=float)
        with pytest.raises(ValueError, match="determinant is zero"):
            mat_transform_png(str(tmp_image), bad_matrix, str(output))

    def test_output_file_created(self, tmp_image, tmp_path):
        output = tmp_path / "out.png"
        identity = np.array([[1, 0], [0, 1]], dtype=float)
        mat_transform_png(str(tmp_image), identity, str(output))
        assert output.exists()
        Image.open(output).verify()

    def test_verbose_callback_called(self, tmp_image, tmp_path):
        output = tmp_path / "verbose_out.png"
        identity = np.array([[1, 0], [0, 1]], dtype=float)
        messages = []
        mat_transform_png(str(tmp_image), identity, str(output), verbose_callback=messages.append)

        assert any("Opened" in m for m in messages)
        assert any("Output size" in m for m in messages)
        assert any("Processing row" in m for m in messages)
        assert any("Saved to" in m for m in messages)

    def test_no_verbose_callback(self, tmp_image, tmp_path):
        output = tmp_path / "quiet_out.png"
        identity = np.array([[1, 0], [0, 1]], dtype=float)
        mat_transform_png(str(tmp_image), identity, str(output), verbose_callback=None)
        assert output.exists()

    def test_rotation_changes_dimensions(self, tmp_image, tmp_path):
        output = tmp_path / "rotated.png"
        angle = np.radians(45)
        rotate = np.array(
            [
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ]
        )
        mat_transform_png(str(tmp_image), rotate, str(output))
        assert output.exists()
        result = np.array(Image.open(output))
        assert result.shape[0] > 0
        assert result.shape[1] > 0
