#!/usr/bin/env python3
"""
Figure 4: Service Grid Hexagonal Layout

Generates a schematic illustration of the hexagonal service grid used in the
DC-MSS-IMT interference study. Shows hexagonal tessellation within a circular
service zone of 1000 km radius, with representative beam footprints.

The figure demonstrates:
- Hexagonal grid spacing driven by beam radius
- Circular service area boundary (1000 km radius)
- Service points at hexagon centers
- Representative beam footprints showing coverage pattern

Technical consistency:
- Beam radius values: 25.700 km (340 km orbit), 39.684 km (525 km orbit)
- Service grid centered at Asunción, Paraguay
- Hexagonal spacing approximately equal to beam radius for efficient coverage
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches


def generate_hexagonal_grid(radius_km, spacing_km):
    """
    Generate hexagonal grid within circular boundary.
    
    Parameters
    ----------
    radius_km : float
        Radius of circular service area in km
    spacing_km : float
        Hexagonal grid spacing in km (approximately beam radius)
    
    Returns
    -------
    points : ndarray
        Array of (x, y) coordinates for grid points within circle
    """
    # Hexagonal grid geometry
    dx = spacing_km
    dy = spacing_km * np.sqrt(3) / 2
    
    # Generate candidate points in rectangular bounding box
    x_max = radius_km + spacing_km
    y_max = radius_km + spacing_km
    
    points = []
    row = 0
    y = -y_max
    while y <= y_max:
        x_offset = (spacing_km / 2) if (row % 2 == 1) else 0
        x = -x_max + x_offset
        while x <= x_max:
            # Filter by circular boundary
            if np.sqrt(x**2 + y**2) <= radius_km:
                points.append([x, y])
            x += dx
        y += dy
        row += 1
    
    return np.array(points)


def plot_service_grid_hexagonal():
    """
    Generate Figure 4: Service grid hexagonal layout.
    """
    # Configuration matching 340 km orbital altitude case
    service_radius_km = 1000
    beam_radius_km = 25.7  # Representative, from 340 km configuration
    
    # Generate hexagonal grid
    grid_points = generate_hexagonal_grid(service_radius_km, beam_radius_km)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot circular service boundary
    service_circle = Circle((0, 0), service_radius_km, 
                           fill=False, edgecolor='black', linewidth=2, 
                           linestyle='--', label='Service area boundary (1000 km)')
    ax.add_patch(service_circle)
    
    # Plot hexagonal cells for subset in center (avoid clutter)
    hex_size_km = beam_radius_km / np.sqrt(3)  # Hexagon circumradius
    hexagons = []
    center_region_radius = 300  # Only show hexagons in central region for clarity
    
    for point in grid_points:
        if np.sqrt(point[0]**2 + point[1]**2) <= center_region_radius:
            hexagon = RegularPolygon(
                point, 6, radius=hex_size_km,
                orientation=0,
                facecolor='lightblue', 
                edgecolor='blue', 
                linewidth=0.8,
                alpha=0.3
            )
            hexagons.append(hexagon)
    
    hex_collection = PatchCollection(hexagons, match_original=True)
    ax.add_collection(hex_collection)
    
    # Plot all grid points (service points)
    ax.scatter(grid_points[:, 0], grid_points[:, 1], 
              s=8, c='blue', marker='o', alpha=0.6, 
              label='Service grid points', zorder=3)
    
    # Highlight a few beam footprints as examples
    example_indices = [len(grid_points)//2, len(grid_points)//2 + 50, 
                       len(grid_points)//2 - 50, len(grid_points)//2 + 100]
    
    for idx in example_indices:
        if idx < len(grid_points):
            point = grid_points[idx]
            if np.sqrt(point[0]**2 + point[1]**2) <= service_radius_km:
                beam_circle = Circle(
                    point, beam_radius_km,
                    fill=False, edgecolor='red', 
                    linewidth=1.5, linestyle='-', alpha=0.7
                )
                ax.add_patch(beam_circle)
    
    # Add center marker for reference (Asunción)
    ax.scatter([0], [0], s=200, c='red', marker='*', 
              edgecolors='black', linewidths=1.5,
              label='Service center (Asunción)', zorder=5)
    
    # Formatting
    ax.set_xlim(-1100, 1100)
    ax.set_ylim(-1100, 1100)
    ax.set_xlabel('Distance East (km)', fontsize=12)
    ax.set_ylabel('Distance North (km)', fontsize=12)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper right', fontsize=10)
    
    # Add annotation explaining beam footprints
    ax.text(0.02, 0.02, 
            f'Hexagonal spacing ≈ {beam_radius_km:.1f} km\n'
            f'Representative beam radius: {beam_radius_km:.1f} km (340 km orbit)\n'
            f'Red circles: Example beam footprints',
            transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'campaigns/mss_d2d_to_mss_adj_study/help_plots/output/service_grid_hexagonal.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")
    
    plt.close()


if __name__ == '__main__':
    plot_service_grid_hexagonal()
