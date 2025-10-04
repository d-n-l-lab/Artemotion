## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Description: Procedural geometry generator for robot links when STL files are missing
##
##############################################################################################
##
import numpy as np
from typing import Tuple


def create_cylinder_geometry(radius: float = 0.05, height: float = 0.2, segments: int = 16) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a cylinder mesh for robot links.

    Args:
        radius: Cylinder radius in meters
        height: Cylinder height in meters
        segments: Number of segments around the cylinder

    Returns:
        vertices: Nx3 array of vertices
        indices: Nx3 array of triangle indices
    """
    vertices = []
    indices = []

    # Create cylinder body vertices
    for i in range(segments + 1):
        angle = (i / segments) * 2 * np.pi
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)

        # Bottom and top vertices
        vertices.append([x, 0, z])
        vertices.append([x, height, z])

    # Create cylinder body triangles
    for i in range(segments):
        base = i * 2

        # Two triangles per segment
        indices.append([base, base + 2, base + 1])
        indices.append([base + 1, base + 2, base + 3])

    # Add caps
    bottom_center = len(vertices)
    vertices.append([0, 0, 0])

    top_center = len(vertices)
    vertices.append([0, height, 0])

    # Bottom cap triangles
    for i in range(segments):
        base = i * 2
        next_base = ((i + 1) % segments) * 2
        indices.append([bottom_center, base, next_base])

    # Top cap triangles
    for i in range(segments):
        base = i * 2 + 1
        next_base = ((i + 1) % segments) * 2 + 1
        indices.append([top_center, next_base, base])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)


def create_box_geometry(width: float = 0.2, height: float = 0.2, depth: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a box mesh for robot base.

    Args:
        width: Box width (X) in meters
        height: Box height (Y) in meters
        depth: Box depth (Z) in meters

    Returns:
        vertices: Nx3 array of vertices
        indices: Nx3 array of triangle indices
    """
    w, h, d = width/2, height/2, depth/2

    # 8 vertices of the box
    vertices = np.array([
        [-w, -h, -d], [w, -h, -d], [w, h, -d], [-w, h, -d],  # Front face
        [-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d],      # Back face
    ], dtype=np.float32)

    # 12 triangles (2 per face)
    indices = np.array([
        # Front
        [0, 1, 2], [0, 2, 3],
        # Back
        [5, 4, 7], [5, 7, 6],
        # Left
        [4, 0, 3], [4, 3, 7],
        # Right
        [1, 5, 6], [1, 6, 2],
        # Bottom
        [4, 5, 1], [4, 1, 0],
        # Top
        [3, 2, 6], [3, 6, 7],
    ], dtype=np.uint32)

    return vertices, indices


def create_robot_link_geometry(link_config: dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create geometry for a robot link based on its configuration.

    Args:
        link_config: Link configuration dict with 'size' parameter

    Returns:
        vertices: Nx3 array of vertices
        indices: Nx3 array of triangle indices
    """
    size = link_config.get('size', {})
    x = size.get('x', 0.1)
    y = size.get('y', 0.2)
    z = size.get('z', 0.1)

    # Determine shape based on proportions
    if link_config.get('name') == 'base':
        # Base is typically a box
        return create_box_geometry(x, y, z)
    else:
        # Links are cylinders
        # Use the longest dimension as height, average of others as radius
        dims = sorted([x, y, z])
        radius = (dims[0] + dims[1]) / 4  # Make it slimmer
        height = dims[2]
        return create_cylinder_geometry(radius, height, segments=12)
