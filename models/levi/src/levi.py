#!/usr/bin/env python3
"""Starter Gmsh model for a hollow box with 2 mm walls."""

from __future__ import annotations

import argparse
from pathlib import Path

import gmsh


MODEL_NAME = "levi_box"
WALL_THICKNESS_MM = 2.0
OUTER_LENGTH_MM = 120.0
OUTER_WIDTH_MM = 80.0
OUTER_HEIGHT_MM = 50.0
MESH_SIZE_MM = 4.0


def add_hollow_box(length: float, width: float, height: float, wall: float) -> None:
    """Build an open-top box with uniform side walls and floor thickness."""
    if wall <= 0:
        raise ValueError("wall thickness must be positive")
    if length <= wall * 2 or width <= wall * 2 or height <= wall:
        raise ValueError("box dimensions must be larger than the wall thickness")

    outer = gmsh.model.occ.addBox(0, 0, 0, length, width, height)

    # Cut the cavity through the top, leaving `wall` mm sides and floor.
    inner = gmsh.model.occ.addBox(
        wall,
        wall,
        wall,
        length - wall * 2,
        width - wall * 2,
        height,
    )

    result, _ = gmsh.model.occ.cut(
        [(3, outer)],
        [(3, inner)],
        removeObject=True,
        removeTool=True,
    )
    gmsh.model.occ.synchronize()

    volume_tags = [tag for dim, tag in result if dim == 3]
    if volume_tags:
        gmsh.model.addPhysicalGroup(3, volume_tags, name="box_body")

    surface_tags = [tag for dim, tag in gmsh.model.getEntities(2)]
    if surface_tags:
        gmsh.model.addPhysicalGroup(2, surface_tags, name="box_shell")


def configure_mesh(mesh_size: float) -> None:
    gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size)
    gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)


def write_model(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    mesh_dimension = 2 if output.suffix.lower() == ".stl" else 3
    gmsh.model.mesh.generate(mesh_dimension)
    gmsh.write(str(output))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=float, default=OUTER_LENGTH_MM)
    parser.add_argument("--width", type=float, default=OUTER_WIDTH_MM)
    parser.add_argument("--height", type=float, default=OUTER_HEIGHT_MM)
    parser.add_argument("--wall", type=float, default=WALL_THICKNESS_MM)
    parser.add_argument("--mesh-size", type=float, default=MESH_SIZE_MM)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "outputs" / f"{MODEL_NAME}.stl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    gmsh.initialize()
    try:
        gmsh.model.add(MODEL_NAME)
        add_hollow_box(args.length, args.width, args.height, args.wall)
        configure_mesh(args.mesh_size)
        write_model(args.output)
    finally:
        gmsh.finalize()

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
