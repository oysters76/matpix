from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Transform:
    name: str
    matrix: np.ndarray
    description: str

    def __hash__(self):
        return hash(self.name)


_angle_45 = np.radians(45)
_angle_30 = np.radians(30)

TRANSFORMS: dict[str, Transform] = {
    "rotate45": Transform(
        name="rotate45",
        matrix=np.array(
            [
                [np.cos(_angle_45), -np.sin(_angle_45)],
                [np.sin(_angle_45), np.cos(_angle_45)],
            ]
        ),
        description="45-degree rotation",
    ),
    "scale2x": Transform(
        name="scale2x",
        matrix=np.array(
            [
                [2, 0],
                [0, 2],
            ]
        ),
        description="Uniform 2x scale",
    ),
    "flip_h": Transform(
        name="flip_h",
        matrix=np.array(
            [
                [-1, 0],
                [0, 1],
            ]
        ),
        description="Horizontal flip (mirror left-right)",
    ),
    "flip_v": Transform(
        name="flip_v",
        matrix=np.array(
            [
                [1, 0],
                [0, -1],
            ]
        ),
        description="Vertical flip (mirror top-bottom)",
    ),
    "squeeze": Transform(
        name="squeeze",
        matrix=np.array(
            [
                [2, 0],
                [0, 0.5],
            ]
        ),
        description="Stretch x 2x, squish y 0.5x",
    ),
    "diamond": Transform(
        name="diamond",
        matrix=np.array(
            [
                [1, -1],
                [1, 1],
            ]
        ),
        description="45-degree rotation + sqrt(2) scale",
    ),
    "reflect": Transform(
        name="reflect",
        matrix=np.array(
            [
                [0, 1],
                [1, 0],
            ]
        ),
        description="Reflection across y=x",
    ),
    "trippy": Transform(
        name="trippy",
        matrix=np.array(
            [
                [1.5, 0.8],
                [0.3, 1.2],
            ]
        ),
        description="Spiral-ish shear",
    ),
    "flat": Transform(
        name="flat",
        matrix=np.array(
            [
                [3, 0],
                [0, 0.1],
            ]
        ),
        description="Near-collapse to horizontal line",
    ),
    "psycho": Transform(
        name="psycho",
        matrix=np.array(
            [
                [np.cos(_angle_30) * 2, -np.sin(_angle_30) + 0.5],
                [np.sin(_angle_30) + 0.3, np.cos(_angle_30) * 1.5],
            ]
        ),
        description="Rotate 30 degrees + skew + scale combo",
    ),
}


def get_transform(name: str) -> Transform:
    if name not in TRANSFORMS:
        valid = ", ".join(sorted(TRANSFORMS))
        raise KeyError(f"Unknown transform '{name}'. Available: {valid}")
    return TRANSFORMS[name]


def list_transforms() -> list[Transform]:
    return sorted(TRANSFORMS.values(), key=lambda t: t.name)


def parse_custom_matrix(spec: str) -> np.ndarray:
    parts = [s.strip() for s in spec.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Matrix must have exactly 4 values (a,b,c,d), got {len(parts)}")
    try:
        values = [float(p) for p in parts]
    except ValueError as err:
        raise ValueError(f"Matrix values must be numbers, got: {spec}") from err
    return np.array(values).reshape(2, 2)
