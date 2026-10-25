import argparse
import json
import os
import sys

import numpy as np

from matpix.core import mat_transform_png
from matpix.transforms import (
    get_transform,
    list_transforms,
    parse_custom_matrix,
)


def _json_out(data):
    print(json.dumps(data))


def _matrix_to_list(mat):
    return [[round(float(v), 6) for v in row] for row in mat]


def _cmd_transform(args) -> int:
    if not os.path.isfile(args.input):
        msg = f"File not found: {args.input}"
        if args.json:
            _json_out({"status": "error", "message": msg})
        else:
            print(msg, file=sys.stderr)
        return 1

    if args.transform:
        try:
            t = get_transform(args.transform)
        except KeyError as e:
            msg = str(e).strip("'\"")
            if args.json:
                _json_out({"status": "error", "message": msg})
            else:
                print(msg, file=sys.stderr)
            return 1
        matrix = t.matrix
        transform_name = t.name
    else:
        try:
            matrix = parse_custom_matrix(args.matrix)
        except ValueError as e:
            msg = str(e)
            if args.json:
                _json_out({"status": "error", "message": msg})
            else:
                print(msg, file=sys.stderr)
            return 1
        transform_name = "custom"

    if args.output:
        output_path = args.output
    else:
        basename = os.path.basename(args.input)
        output_path = f"transformed_{basename}"

    verbose_callback = None
    if args.verbose:

        def verbose_callback(msg):
            print(msg, file=sys.stderr)

    try:
        mat_transform_png(args.input, matrix, output_path, verbose_callback)
    except ValueError as e:
        msg = str(e)
        if args.json:
            _json_out({"status": "error", "message": msg})
        else:
            print(msg, file=sys.stderr)
        return 1

    if args.json:
        _json_out(
            {
                "status": "ok",
                "output_file": output_path,
                "transform": transform_name,
                "matrix": _matrix_to_list(matrix),
            }
        )
    else:
        print(f"Saved to {output_path}")

    return 0


def _cmd_list(args) -> int:
    transforms = list_transforms()

    if args.json:
        _json_out(
            [
                {
                    "name": t.name,
                    "description": t.description,
                    "matrix": _matrix_to_list(t.matrix),
                }
                for t in transforms
            ]
        )
    else:
        print("Available transforms:\n")
        max_name = max(len(t.name) for t in transforms)
        for t in transforms:
            print(f"  {t.name:<{max_name}}  {t.description}")

    return 0


def _cmd_info(args) -> int:
    try:
        t = get_transform(args.name)
    except KeyError as e:
        msg = str(e).strip("'\"")
        if args.json:
            _json_out({"status": "error", "message": msg})
        else:
            print(msg, file=sys.stderr)
        return 1

    det = float(np.linalg.det(t.matrix))

    if args.json:
        _json_out(
            {
                "name": t.name,
                "description": t.description,
                "matrix": _matrix_to_list(t.matrix),
                "determinant": round(det, 6),
            }
        )
    else:
        print(f"Transform: {t.name}")
        print(f"Description: {t.description}")
        print("Matrix:")
        for row in t.matrix:
            print(f"  [{row[0]:8.4f}  {row[1]:8.4f}]")
        print(f"Determinant: {det:.4f}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="matpix",
        description="Apply 2D linear matrix transformations to images",
    )
    subparsers = parser.add_subparsers(dest="command")

    # transform
    p_transform = subparsers.add_parser("transform", help="Apply a transformation to an image")
    p_transform.add_argument("input", help="Input image file")
    group = p_transform.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--transform", help="Named transform (use 'matpix list' to see all)")
    group.add_argument("-m", "--matrix", help="Custom 2x2 matrix as 'a,b,c,d' → [[a,b],[c,d]]")
    p_transform.add_argument("-o", "--output", help="Output file (default: transformed_<input>)")
    p_transform.add_argument("--verbose", action="store_true", help="Show progress")
    p_transform.add_argument("--json", action="store_true", help="JSON output for programmatic use")

    # list
    p_list = subparsers.add_parser("list", help="List available transforms")
    p_list.add_argument("--json", action="store_true", help="JSON output")

    # info
    p_info = subparsers.add_parser("info", help="Show details of a transform")
    p_info.add_argument("name", help="Transform name")
    p_info.add_argument("--json", action="store_true", help="JSON output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    handlers = {
        "transform": _cmd_transform,
        "list": _cmd_list,
        "info": _cmd_info,
    }

    try:
        return handlers[args.command](args)
    except Exception as e:
        use_json = getattr(args, "json", False)
        if use_json:
            _json_out({"status": "error", "message": str(e)})
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1
