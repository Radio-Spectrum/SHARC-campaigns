#!/usr/bin/env python3
"""
Figure 5: Satellite Eligibility and Service Margin

Generates a schematic illustration showing the eligible satellite selection
concept with the -200 km margin parameter used in the service grid methodology.

The figure demonstrates:
- Circular service area (1000 km radius)
- Eligibility zone with -200 km margin (1200 km effective radius)
- Satellites within eligibility zone can serve edge service points
- Geometric rationale for margin parameter

Technical consistency:
- Service area: 1000 km radius circular zone
- Eligibility margin: -200 km (expands eligibility zone to 1200 km)
- Minimum elevation constraint: 5 degrees from Earth station
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Wedge
import matplotlib.patches as mpatches


def plot_satellite_eligibility():
    """
    Generate Figure 5: Satellite eligibility and margins.
    """
    # Configuration
    service_radius_km = 1000
    margin_km = 200  # Absolute value of -200 km margin
    eligibility_radius_km = service_radius_km + margin_km
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot Earth station position (center, Asunción)
    ax.scatter([0], [0], s=300, c='red', marker='*', 
              edgecolors='black', linewidths=2,
              label='Earth station (Asunción)', zorder=10)
    
    # Plot service area boundary
    service_circle = Circle((0, 0), service_radius_km, 
                           fill=True, facecolor='lightblue', 
                           edgecolor='blue', linewidth=2.5, 
                           linestyle='-', alpha=0.3,
                           label='Service area (1000 km)')
    ax.add_patch(service_circle)
    
    # Plot eligibility zone boundary
    eligibility_circle = Circle((0, 0), eligibility_radius_km, 
                               fill=False, 
                               edgecolor='green', linewidth=2.5, 
                               linestyle='--', 
                               label=f'Eligibility zone ({eligibility_radius_km} km)')
    ax.add_patch(eligibility_circle)
    
    # Plot margin region (annulus between service and eligibility)
    margin_wedge = Wedge((0, 0), eligibility_radius_km, 0, 360,
                        width=margin_km, 
                        facecolor='lightgreen', alpha=0.2,
                        edgecolor='none',
                        label=f'Eligibility margin (-200 km)')
    ax.add_patch(margin_wedge)
    
    # Example satellites
    # Eligible satellite outside service area but within eligibility zone
    sat1_pos = np.array([1100, 300])
    ax.scatter([sat1_pos[0]], [sat1_pos[1]], 
              s=250, c='green', marker='^', 
              edgecolors='darkgreen', linewidths=2,
              label='Eligible satellite (outside service, within eligibility)', 
              zorder=8)
    
    # Eligible satellite inside service area
    sat2_pos = np.array([600, -600])
    ax.scatter([sat2_pos[0]], [sat2_pos[1]], 
              s=250, c='green', marker='^', 
              edgecolors='darkgreen', linewidths=2,
              zorder=8)
    
    # Ineligible satellite outside eligibility zone
    sat3_pos = np.array([-1400, 400])
    ax.scatter([sat3_pos[0]], [sat3_pos[1]], 
              s=250, c='red', marker='v', 
              edgecolors='darkred', linewidths=2,
              label='Ineligible satellite (outside eligibility zone)', 
              zorder=8)
    
    # Example edge service point that can be served by sat1
    edge_point = np.array([950, 280])
    ax.scatter([edge_point[0]], [edge_point[1]], 
              s=150, c='orange', marker='o', 
              edgecolors='darkorange', linewidths=2,
              label='Edge service point', zorder=9)
    
    # Connection line from eligible satellite to edge point
    arrow1 = FancyArrowPatch(sat1_pos, edge_point,
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=2, color='green', alpha=0.7,
                            linestyle='--')
    ax.add_patch(arrow1)
    
    # Annotations
    # Service radius annotation
    ax.annotate('', xy=(service_radius_km * 0.707, service_radius_km * 0.707), 
               xytext=(0, 0),
               arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
    ax.text(service_radius_km * 0.707 / 2, service_radius_km * 0.707 / 2 + 80, 
           '1000 km', fontsize=11, color='blue', weight='bold',
           ha='center', rotation=45)
    
    # Eligibility radius annotation
    ax.annotate('', xy=(eligibility_radius_km * 0.707, -eligibility_radius_km * 0.707), 
               xytext=(0, 0),
               arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
    ax.text(eligibility_radius_km * 0.707 / 2, -eligibility_radius_km * 0.707 / 2 - 80, 
           '1200 km', fontsize=11, color='green', weight='bold',
           ha='center', rotation=-45)
    
    # Margin width annotation
    margin_angle_rad = np.deg2rad(110)
    r1 = service_radius_km
    r2 = eligibility_radius_km
    p1 = np.array([r1 * np.cos(margin_angle_rad), r1 * np.sin(margin_angle_rad)])
    p2 = np.array([r2 * np.cos(margin_angle_rad), r2 * np.sin(margin_angle_rad)])
    
    ax.annotate('', xy=p2, xytext=p1,
               arrowprops=dict(arrowstyle='<->', color='darkgreen', lw=2))
    ax.text((p1[0] + p2[0])/2 - 100, (p1[1] + p2[1])/2, 
           '200 km\nmargin', fontsize=10, color='darkgreen', weight='bold',
           ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Formatting
    ax.set_xlim(-1600, 1600)
    ax.set_ylim(-1600, 1600)
    ax.set_xlabel('Distance East (km)', fontsize=12)
    ax.set_ylabel('Distance North (km)', fontsize=12)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    
    # Explanation text box
    explanation_text = (
        'Eligibility margin parameter: -200 km\n'
        'Allows satellites outside the strict service boundary\n'
        'to serve edge service points when geometrically favorable.\n'
        'Additional constraint: minimum elevation = 5 degrees.'
    )
    ax.text(0.02, 0.02, explanation_text,
            transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'campaigns/mss_d2d_to_mss_adj_study/help_plots/output/satellite_eligibility.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")
    
    plt.close()


if __name__ == '__main__':
    plot_satellite_eligibility()
