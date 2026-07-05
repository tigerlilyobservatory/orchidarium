#!/usr/bin/env python3
"""Starter Gmsh model for a hollow box with 2 mm walls."""

from __future__ import annotations

import argparse
from pathlib import Path

import gmsh


show_bounds = False

class BoundedObject:
    """Base class for objects with a bounding box."""
    
    def __init__(self, length: float, width: float, height: float, show_bounds=None) -> None:
        self.show_bounds = show_bounds
        self.length = length
        self.width = width
        self.height = height

    @property
    def bounding_box(self) -> tuple[float, float, float, float, float, float]:
        """Return the bounding box as (xmin, ymin, zmin, xmax, ymax, zmax)."""
        return (0.0, 0.0, 0.0, self.length, self.width, self.height)

    def draw(self, x, y, z, x_anchor="center", y_anchor="center", z_anchor="bottom") -> None:
        """Draw the object at the specified position with the given anchor point."""
        # Calculate the position based on the anchor points
        if x_anchor == "center":
            x -= self.length / 2
        elif x_anchor == "right":
            x -= self.length

        if y_anchor == "center":
            y -= self.width / 2
        elif y_anchor == "back":
            y -= self.width

        if z_anchor == "center":
            z -= self.height / 2
        elif z_anchor == "top":
            z -= self.height
        
        if self.show_bounds or show_bounds:
            # Draw the bounding box
            gmsh.model.occ.addBox(x, y, z, self.length, self.width, self.height)
        
        self.draw_at_position(x, y, z)

class MotorMount(BoundedObject):
    """A simple motor mount with a bounding box."""

    self.mount_length, self.mount_width, self.mount_height = 100, 75.5, 8
    self.total_height=87.5
    self.motor_diameter=84.5
    self.motor_width=200
    self.width_to_mount=93
    self.mount_hole_offset = 4.34
    self.mount_hole_diameter = 10.14

    def __init__(self, show_bounds=None) -> None:

        super().__init__(length, width, height, show_bounds)

    def draw_at_position(self, x: float, y: float, z: float) -> None:
        gmsh.model.occ.addBox(x, y, z, self.length, self.width, self.height)


left_wall = Panel(
    Component(Motor(), 15, 0, 0, x_anchor="left", y_anchor="back", z_anchor="bottom"),
    Component()



)



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
