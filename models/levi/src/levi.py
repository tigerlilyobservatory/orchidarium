#!/usr/bin/env python3
"""PythonSCAD starter model for the Levi box."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from pythonscad import cube, export, show


MODEL_NAME = "levi_box"
WALL_THICKNESS_MM = 2.0
OUTER_LENGTH_MM = 120.0
OUTER_WIDTH_MM = 80.0
OUTER_HEIGHT_MM = 50.0
CUT_EPSILON_MM = 0.01


@dataclass(frozen=True)
class HollowBox:
    length: float = OUTER_LENGTH_MM
    width: float = OUTER_WIDTH_MM
    height: float = OUTER_HEIGHT_MM
    wall: float = WALL_THICKNESS_MM

    def validate(self) -> None:
        if self.wall <= 0:
            raise ValueError("wall thickness must be positive")
        if self.length <= self.wall * 2:
            raise ValueError("length must be greater than twice the wall thickness")
        if self.width <= self.wall * 2:
            raise ValueError("width must be greater than twice the wall thickness")
        if self.height <= self.wall:
            raise ValueError("height must be greater than the wall thickness")

    @property
    def inner_size(self) -> list[float]:
        return [
            self.length - self.wall * 2,
            self.width - self.wall * 2,
            self.height - self.wall + CUT_EPSILON_MM,
        ]

    @property
    def outer_size(self) -> list[float]:
        return [self.length, self.width, self.height]

    def model(self):
        self.validate()
        outer = cube(self.outer_size, center=False)
        inner = cube(self.inner_size, center=False).translate(
            [self.wall, self.wall, self.wall]
        )
        return outer - inner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=float, default=OUTER_LENGTH_MM)
    parser.add_argument("--width", type=float, default=OUTER_WIDTH_MM)
    parser.add_argument("--height", type=float, default=OUTER_HEIGHT_MM)
    parser.add_argument("--wall", type=float, default=WALL_THICKNESS_MM)
    parser.add_argument(
        "--export",
        type=Path,
        help="Optional output path for PythonSCAD export, e.g. levi_box.stl.",
    )
    return parser.parse_args()


def build_box(args: argparse.Namespace):
    return HollowBox(
        length=args.length,
        width=args.width,
        height=args.height,
        wall=args.wall,
    ).model()


def main() -> None:
    args = parse_args()
    box = build_box(args)

    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        export(box, str(args.export))
        print(f"Wrote {args.export}")
        return

    show(box)


if __name__ == "__main__":
    main()
