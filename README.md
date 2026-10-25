# matpix

Apply 2D linear matrix transformations to images from the command line.

matpix takes an input image and a 2x2 transformation matrix, applies the linear transformation to every pixel in Cartesian space, and writes the result.

## Installation

```bash
pip install -e .
```

## Usage

### Apply a named transform

```bash
matpix transform photo.png -t rotate45
matpix transform photo.png -t scale2x -o big_photo.png
```

### Apply a custom matrix

Pass four values as `a,b,c,d` to define the matrix `[[a,b],[c,d]]`:

```bash
matpix transform photo.png -m "1.5,0.8,0.3,1.2" -o warped.png
```

### List available transforms

```bash
matpix list
```

```
Available transforms:

  diamond   45-degree rotation + sqrt(2) scale
  flat      Near-collapse to horizontal line
  flip_h    Horizontal flip (mirror left-right)
  flip_v    Vertical flip (mirror top-bottom)
  psycho    Rotate 30 degrees + skew + scale combo
  reflect   Reflection across y=x
  rotate45  45-degree rotation
  scale2x   Uniform 2x scale
  squeeze   Stretch x 2x, squish y 0.5x
  trippy    Spiral-ish shear
```

### Inspect a transform

```bash
matpix info rotate45
```

```
Transform: rotate45
Description: 45-degree rotation
Matrix:
  [  0.7071   -0.7071]
  [  0.7071    0.7071]
Determinant: 1.0000
```

### JSON output (for scripts and agents)

Every subcommand supports `--json` for machine-readable output:

```bash
matpix transform photo.png -t rotate45 --json
# {"status": "ok", "output_file": "transformed_photo.png", "transform": "rotate45", "matrix": [[0.707107, -0.707107], [0.707107, 0.707107]]}

matpix list --json
# [{"name": "diamond", ...}, ...]

matpix info rotate45 --json
# {"name": "rotate45", "description": "...", "matrix": [...], "determinant": 1.0}
```

### Verbose mode

```bash
matpix transform photo.png -t rotate45 --verbose
```

Progress is printed to stderr so it doesn't interfere with `--json` output on stdout.

## Library usage

```python
from matpix import mat_transform_png
import numpy as np

matrix = np.array([[2, 0], [0, 2]])
mat_transform_png("input.png", matrix, "output.png")
```

## License

MIT
