from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

#constants
g = 9.81 #m/s^2
samples = 200 #minimum number of intervals per section

#equation connecting two points on the track
def section(x, x1, x2, y1, y2):
    return y1 + (y2 - y1)/2 * (1 - np.cos(np.pi * (x - x1)/(x2 - x1)))

#inputs and track length check
while True:
    try:
        distance = float(input("Horizontal distance (m): "))
        height = float(input("Initial peak height (m): "))
        hills = int(input("Number of additional hills (at least 6): "))
        mass = float(input("Mass (kg): "))
        speed = float(input("Desired final speed (m/s, between 0 and 10): "))
    except ValueError:
        print("Enter numbers only, with a whole number for the hill count.")
        continue

    if not np.all(np.isfinite([distance, height, mass, speed])):
        print("Enter finite numbers.")
        continue
    if distance <= 0 or height <= 0 or mass <= 0:
        print("Distance, height, and mass must be positive.")
        continue
    if hills < 6:
        print("There must be at least six additional hills.")
        continue
    if speed <= 0 or speed >= 10:
        print("Final speed must be greater than 0 and less than 10 m/s.")
        continue

    final_height = height - speed**2/(2*g)
    if final_height < 0:
        print("Final height would be below ground. Increase height or decrease speed.")
        continue

    #random widths for the hills between 20% and 85% of the distance
    widths = []
    for n in range(2*hills):
        widths.append(np.random.uniform(0.5, 1.5))
    total_width = sum(widths)

    x_points = [0, 0.1 * distance, 0.2 * distance]
    for n in range(2*hills):
        x_points.append(x_points[-1] + 0.65 * distance * widths[n]/total_width)
    x_points.append(distance)

    #random peak heights, all below the initial peak
    y_points = [0, height, 0]
    for n in range(hills):
        hill_height = np.random.uniform(0, height)
        while hill_height <= 0 or hill_height >= height:
            hill_height = np.random.uniform(0, height)
        y_points.append(hill_height)
        y_points.append(0) #valley height is calculated below
    y_points.append(final_height)

    #each valley must be lower than both neighboring peaks
    for n in range(2, len(y_points)-1, 2):
        limit = min(y_points[n-1], y_points[n+1])
        if limit > 0:
            valley_height = np.random.uniform(0, limit)
            while valley_height <= 0 or valley_height >= limit:
                valley_height = np.random.uniform(0, limit)
            y_points[n] = valley_height
        #If the finish is at ground level, the last valley stays at zero.

    #find the shortest section to set uniform spacing
    shortest = distance
    for n in range(len(x_points)-1):
        width = x_points[n+1] - x_points[n]
        if width < shortest:
            shortest = width
    intervals = int(np.ceil(distance/shortest)) * samples
    x = np.linspace(0, distance, intervals + 1)
    y = []

    #calculate the height at each x using the correct piece
    index = 0
    for n in range(len(x)):
        while x[n] > x_points[index+1] and index < len(x_points)-2:
            index += 1
        y.append(section(x[n], x_points[index], x_points[index+1],
                         y_points[index], y_points[index+1]))

    #forward differentiation
    slope = []
    slope.append((y[1] - y[0])/(x[1] - x[0]))

    #central differentiation
    for n in range(1, len(x)-1):
        slope.append((y[n+1] - y[n-1])/(x[n+1] - x[n-1]))

    #backward differentiation
    n = len(x)-1
    slope.append((y[n] - y[n-1])/(x[n] - x[n-1]))

    #trapezoidal rule for actual track length
    length = 0
    for n in range(len(x)-1):
        f1 = np.sqrt(1 + slope[n]**2)
        f2 = np.sqrt(1 + slope[n+1]**2)
        length += (x[n+1] - x[n])/2 * (f1 + f2)

    if length >= 300 and length <= 1200:
        break
    print(f"Actual track length: {length:.2f} m. It must be between 300 and 1200 m.")
    print("Adjust distance, height, or hill count and enter all five inputs again.")

#energy calculations, released from rest after the powered lift
max_pe = mass * g * height
final_ke = mass * g * (height - final_height)
final_speed = np.sqrt(2 * final_ke/mass)

print(f"\nActual track length: {length:.2f} m")
print(f"Total Bumps: {hills + 1}")
print(f"Maximum potential energy: {max_pe:.2f} J")
print(f"Final kinetic energy: {final_ke:.2f} J")
print(f"Calculated final speed: {final_speed:.4f} m/s")

#track plot
plt.figure(figsize=(12, 6))
plt.plot(x, y, color="purple", label="Track")
plt.scatter(x_points[1:-1], y_points[1:-1], color="green", label="Peaks and valleys")
plt.scatter(0, 0, color="black", marker="s", label="Start")
plt.scatter(distance, final_height, color="red", marker="s", label="Finish")
plt.xlabel("Horizontal distance, x (m)")
plt.ylabel("Height, y (m)")
plt.title("Roller Coaster Track")
plt.ylim(-0.08 * height, 1.65 * height)
plt.legend(loc="upper left")

#results above the track
results = (f"Track length: {length:.2f} m\nTotal Bumps: {hills + 1}\nMass: {mass:g} kg\n"
           f"Maximum PE: {max_pe:.2f} J\nFinal KE: {final_ke:.2f} J\n"
           f"Final speed: {final_speed:.2f} m/s")
plt.text(distance, 1.6 * height, results, ha="right", va="top")
plt.tight_layout()

output = Path(__file__).with_name("rollercoaster.png")
plt.savefig(output, dpi=200)
print(f"Plot saved to: {output}")
plt.show()
