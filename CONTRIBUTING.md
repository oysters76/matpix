# Contributing to matpix

## Getting started

1. Clone the repo and create a virtual environment:

```bash
git clone <repo-url>
cd matpix
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Verify the install:

```bash
matpix list
```

## Project structure

```
src/matpix/
  __init__.py       Package root and public API
  __main__.py       python -m matpix support
  core.py           Transform engine (pixel mapping logic)
  transforms.py     Named transform registry
  cli.py            CLI interface (argparse)
```

## Adding a new transform

1. Open `src/matpix/transforms.py`
2. Add a new entry to the `TRANSFORMS` dict:

```python
"my_transform": Transform(
    name="my_transform",
    matrix=np.array([
        [a, b],
        [c, d],
    ]),
    description="Short description of the effect",
),
```

3. Verify it shows up: `matpix list`
4. Test it: `matpix transform test_image.png -t my_transform`

## Code style

- Keep dependencies minimal — stdlib + numpy + Pillow only.
- All CLI output goes to stdout; progress and errors go to stderr.
- Every subcommand must support `--json` for programmatic use.

## Submitting changes

1. Fork the repo and create a feature branch.
2. Make your changes.
3. Run `matpix list` and a test transform to verify nothing is broken.
4. Open a pull request with a clear description of the change.
