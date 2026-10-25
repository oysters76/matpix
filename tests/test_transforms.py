import dataclasses

import numpy as np
import pytest

from matpix.transforms import (
    TRANSFORMS,
    Transform,
    get_transform,
    list_transforms,
    parse_custom_matrix,
)


class TestTransformDataclass:
    def test_frozen(self):
        t = Transform(name="test", matrix=np.eye(2), description="test")
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.name = "changed"

    def test_hash_by_name(self):
        t1 = Transform(name="a", matrix=np.eye(2), description="one")
        t2 = Transform(name="a", matrix=np.zeros((2, 2)), description="two")
        assert hash(t1) == hash(t2)

    def test_different_names_different_hash(self):
        t1 = Transform(name="a", matrix=np.eye(2), description="one")
        t2 = Transform(name="b", matrix=np.eye(2), description="one")
        assert hash(t1) != hash(t2)


class TestTransformsRegistry:
    def test_contains_10_transforms(self):
        assert len(TRANSFORMS) == 10

    def test_all_names_match_keys(self):
        for key, t in TRANSFORMS.items():
            assert t.name == key

    def test_all_matrices_are_2x2(self):
        for t in TRANSFORMS.values():
            assert t.matrix.shape == (2, 2)

    def test_all_matrices_have_nonzero_determinant(self):
        for t in TRANSFORMS.values():
            det = np.linalg.det(t.matrix)
            assert abs(det) > 1e-10, f"{t.name} has near-zero determinant: {det}"

    def test_all_have_descriptions(self):
        for t in TRANSFORMS.values():
            assert len(t.description) > 0

    @pytest.mark.parametrize(
        "name",
        [
            "rotate45",
            "scale2x",
            "flip_h",
            "flip_v",
            "squeeze",
            "diamond",
            "reflect",
            "trippy",
            "flat",
            "psycho",
        ],
    )
    def test_expected_transforms_exist(self, name):
        assert name in TRANSFORMS


class TestGetTransform:
    def test_valid_name(self):
        t = get_transform("rotate45")
        assert t.name == "rotate45"
        assert t.matrix.shape == (2, 2)

    def test_invalid_name_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown transform"):
            get_transform("nonexistent")

    def test_error_message_lists_valid_names(self):
        with pytest.raises(KeyError, match="rotate45"):
            get_transform("bad_name")


class TestListTransforms:
    def test_returns_all_transforms(self):
        result = list_transforms()
        assert len(result) == 10

    def test_sorted_by_name(self):
        result = list_transforms()
        names = [t.name for t in result]
        assert names == sorted(names)

    def test_returns_transform_objects(self):
        result = list_transforms()
        for t in result:
            assert isinstance(t, Transform)


class TestParseCustomMatrix:
    def test_valid_integers(self):
        mat = parse_custom_matrix("1,2,3,4")
        expected = np.array([[1, 2], [3, 4]], dtype=float)
        np.testing.assert_array_equal(mat, expected)

    def test_valid_floats(self):
        mat = parse_custom_matrix("1.5,0.8,0.3,1.2")
        assert mat.shape == (2, 2)
        assert mat[0, 0] == pytest.approx(1.5)
        assert mat[0, 1] == pytest.approx(0.8)

    def test_handles_whitespace(self):
        mat = parse_custom_matrix(" 1 , 2 , 3 , 4 ")
        expected = np.array([[1, 2], [3, 4]], dtype=float)
        np.testing.assert_array_equal(mat, expected)

    def test_negative_values(self):
        mat = parse_custom_matrix("-1,0,0,1")
        assert mat[0, 0] == pytest.approx(-1.0)

    def test_too_few_values(self):
        with pytest.raises(ValueError, match="exactly 4 values"):
            parse_custom_matrix("1,2,3")

    def test_too_many_values(self):
        with pytest.raises(ValueError, match="exactly 4 values"):
            parse_custom_matrix("1,2,3,4,5")

    def test_non_numeric_values(self):
        with pytest.raises(ValueError, match="must be numbers"):
            parse_custom_matrix("a,b,c,d")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="exactly 4 values"):
            parse_custom_matrix("")
