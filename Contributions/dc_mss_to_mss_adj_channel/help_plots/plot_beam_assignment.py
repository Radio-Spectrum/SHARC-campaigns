#!/usr/bin/env python3
"""
Figure 6: Beam Assignment and Footprints (Best-Server Selection)

Generates a schematic illustration showing the best-server beam assignment
methodology based on elevation angle.

The figure demonstrates:
- Multiple satellites visible from service points
- Best-server selection based on maximum elevation angle
- Beam pointing to selected service points
- Resulting beam footprints with radius from -7 dB antenna contour

Technical consistency:
- Best-server rule: highest elevation angle wins
- Beam radius: 25.700 km (340 km), 39.684 km (525 km)
- Service points in hexagonal grid
- Each service point served by one satellite
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import matplotlib.patches as mpatches


def plot_beam_assignment():
    """
    Generate Figure 6: Beam assignment and footprints.
    """
    # Configuration
    beam_radius_km = 25.7  # From 340 km configuration
    
    # Service points (simplified subset)
    service_points = np.array([
        [0, 0],
        [50, 0],
        [-50, 0],
        [0, 50],
        [0, -50],
        [50, 50],
        [-50, -50],
        [100, 0],
        [-100, 0],
    ])
    
    # Satellites (simplified, showing 3 visible satellites from different positions)
    # Format: [x, y, label, color]
    satellites = [
        {'pos': np.array([-100, 150]), 'label': 'Sat A', 'color': 'blue', 
         'serves': [2, 3, 6]},  # Indices of service points it serves
        {'pos': np.array([120, 120]), 'label': 'Sat B', 'color': 'green',
         'serves': [1, 4, 5]},
        {'pos': np.array([0, -150]), 'label': 'Sat C', 'color': 'purple',
         'serves': [0, 7, 8]},
    ]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot service points
    ax.scatter(service_points[:, 0], service_points[:, 1], 
              s=120, c='orange', marker='o', 
              edgecolors='darkorange', linewidths=2,
              label='Service grid points', zorder=5)
    
    # Plot satellites and their beam assignments
    for sat in satellites:
        sat_pos = sat['pos']
        sat_color = sat['color']
        sat_label = sat['label']
        serves_indices = sat['serves']
        
        # Plot satellite
        ax.scatter([sat_pos[0]], [sat_pos[1]], 
                  s=300, c=sat_color, marker='^', 
                  edgecolors='black', linewidths=2,
                  label=sat_label, zorder=10)
        
        # Plot beams to served points
        for idx in serves_indices:
            point = service_points[idx]
            
            # Arrow from satellite to service point
            arrow = FancyArrowPatch(sat_pos, point,
                                  arrowstyle='->', mutation_scale=15, 
                                  linewidth=1.5, color=sat_color, 
                                  alpha=0.6, linestyle='--')
            ax.add_patch(arrow)
            
            # Beam footprint circle around service point
            beam_circle = Circle(point, beam_radius_km,
                               fill=False, edgecolor=sat_color, 
                               linewidth=2, linestyle='-', alpha=0.7)
            ax.add_patch(beam_circle)
    
    # Add an example of competing satellites for one service point
    # Show dashed lines from other satellites to demonstrate why one was selected
    example_point_idx = 1
    example_point = service_points[example_point_idx]
    
    # Sat A could see this point but has lower elevation than Sat B
    sat_a_pos = satellites[0]['pos']
    competing_arrow = FancyArrowPatch(sat_a_pos, example_point,
                                     arrowstyle='->', mutation_scale=12, 
                                     linewidth=1.2, color='gray', 
                                     alpha=0.4, linestyle=':')
    ax.add_patch(competing_arrow)
    
    # Annotation explaining best-server selection
    ax.text(example_point[0] + 35, example_point[1] + 15, 
           'Best server:\nSat B (higher elevation)', 
           fontsize=9, color='green', weight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    # Arrow annotation for beam radius
    ref_point = service_points[0]
    radius_end = ref_point + np.array([beam_radius_km * 0.707, beam_radius_km * 0.707])
    ax.annotate('', xy=radius_end, xytext=ref_point,
               arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax.text(ref_point[0] + 12, ref_point[1] + 22, 
           f'Beam radius\n{beam_radius_km:.1f} km\n(-7 dB contour)', 
           fontsize=9, color='purple', weight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    # Formatting
    ax.set_xlim(-180, 180)
    ax.set_ylim(-200, 200)
    ax.set_xlabel('Distance East (km)', fontsize=12)
    ax.set_ylabel('Distance North (km)', fontsize=12)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    
    # Title and explanation
    title_text = 'Beam Assignment using Best-Server Selection (Highest Elevation)'
    ax.set_title(title_text, fontsize=13, weight='bold', pad=15)
    
    explanation_text = (
        'Beam assignment methodology:\n'
        '1. For each service point, elevation angle to all visible satellites is computed\n'
        '2. The satellite with highest elevation is selected as the serving satellite\n'
        '3. Beam is pointed to that service point with radius from -7 dB antenna contour\n'
        '4. Gray dotted line shows competing satellite with lower elevation (not selected)'
    )
    ax.text(0.02, 0.02, explanation_text,
            transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'campaigns/mss_d2d_to_mss_adj_study/help_plots/output/beam_assignment.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")
    
    plt.close()


if __name__ == '__main__':
    plot_beam_assignment()
