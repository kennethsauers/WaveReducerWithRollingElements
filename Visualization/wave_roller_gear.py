import matplotlib.pyplot as plt
import numpy as np

# Parameters (You can adjust these as needed)
roller_diameter = 5  # mm
rollers_num = 12
cycloid_outer_diameter = 60 # mm (will be ignored if lower then minimum) 
input_shaft_diameter = 5  # mm

# Function to plot cycloidal points
def cycloid_points(ecc, roll_r, wave_gen_r, rollers_num, cav_num, res = 500):
    points = []
    for i in range(res):
        theta = (i / res) * 2 * np.pi

        s_rol = np.sqrt((roll_r + wave_gen_r) ** 2 - (ecc * np.sin(cav_num * theta)) ** 2)
        l_rol = ecc * np.cos(cav_num * theta) + s_rol
        xi = np.arctan2(ecc * cav_num * np.sin(cav_num * theta), s_rol)

        x = l_rol * np.sin(theta) + roll_r * np.sin(theta + xi)
        y = l_rol * np.cos(theta) + roll_r * np.cos(theta + xi)

        points.append((x, y))
    points.append(points[0])  # Close the loop

    return np.array(points)

# Function to draw a circle
def draw_circle(ax, center, radius, **kwargs):
    circle = plt.Circle(center, radius, **kwargs)
    ax.add_patch(circle)

# Function to plot rollers
def plot_rols(ax, cy_r, wave_gen_r, roll_r, ecc, rollers_num, cav_num):
    R = cy_r - ecc
    theta = np.linspace(0, 2 * np.pi, rollers_num, endpoint=False)
    for t in theta:
        s_rol = np.sqrt((roll_r + wave_gen_r) ** 2 - (ecc * np.sin(cav_num * t)) ** 2)
        l_rol = ecc * np.cos(cav_num * t) + s_rol
        x = l_rol * np.sin(t)
        y = l_rol * np.cos(t)
        draw_circle(ax, (x, y), roll_r, fill=True, color='orange', alpha=0.7)

# Calculate some additional parameters
ecc = 0.2 * roller_diameter  # Eccentricity (Cycloidal Modulus * Roller Diameter)
cav_num = rollers_num + 1 # Number of Cycloids (Rollers num + 1)
cy_r_min = (1.1 * roller_diameter) / np.sin(np.pi / cav_num) + 2 * ecc # Minimum outer Cycloid radius
cy_r = max(cycloid_outer_diameter / 2, cy_r_min)  # Outer Cycloid Radius
wave_gen_r = (cy_r - 2 * ecc) - roller_diameter  # Wave Generator Radius
roll_r = roller_diameter / 2  # Roller Radius

# Create a plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')
ax.set_xlim(-cy_r - 10, cy_r + 10)
ax.set_ylim(-cy_r - 10, cy_r + 10)
ax.set_title("Wave Gear with Rollers, Separator, and Wave Generator")

# Plot Cycloidal Ring Gear
cycloid = cycloid_points(ecc, roll_r, wave_gen_r, rollers_num, cav_num)
ax.plot(cycloid[:, 0], cycloid[:, 1], label='Cycloidal Ring Gear', color='blue')

# Plot Separator
sep_width = 2.2 * ecc
sep_middle_radius = wave_gen_r + roll_r
sep_outer_radius = sep_middle_radius + sep_width / 2
sep_inner_radius = sep_middle_radius - sep_width / 2
draw_circle(ax, (0, 0), sep_outer_radius, fill=False, linestyle='--', color='green', label='Separator')
draw_circle(ax, (0, 0), sep_inner_radius, fill=False, linestyle='--', color='green')

# Plot Rollers
plot_rols(ax, cy_r, wave_gen_r, roll_r, ecc, rollers_num, rollers_num + 1)

# Plot Wave Generator Diameter with Eccentricity
draw_circle(ax, (0, ecc), wave_gen_r, fill=False, linestyle='-.', color='red', label='Wave Generator')

# Plot Input Shaft Hole
draw_circle(ax, (0, 0), input_shaft_diameter / 2, fill=False, color='purple', linestyle=':', label='Input Shaft')

# Show legend
ax.legend(loc='upper right')

# Display the plot
plt.show()