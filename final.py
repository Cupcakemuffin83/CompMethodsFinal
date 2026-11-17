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
print("Welcome to the Rollercoaster generator!!")
while True:
    try:
        distance = float(input("\nHorizontal start-to-finish distance (m; greater than 0; curved track must be 300-1200 m): "))
    except ValueError:
        print("Distance must be a finite number greater than 0. Restarting all inputs.")
        continue
    if not np.isfinite(distance) or distance <= 0 or distance >= 1200:
        print("Distance must be a finite number greater than 0 and less than 1200. Restarting all inputs.")
        continue

    try:
        height = float(input("Initial peak height above ground (m; greater than 0): "))
    except ValueError:
        print("Height must be a finite number greater than 0. Restarting all inputs.")
        continue
    if not np.isfinite(height) or height <= 0:
        print("Height must be a finite number greater than 0. Restarting all inputs.")
        continue

    try:
        hills = int(input("Total hills, including the initial peak (whole number; at least 5): "))
    except ValueError:
        print("Total hills must be a whole number of at least 5. Restarting all inputs.")
        continue
    if hills < 5:
        print("Total hills must be a whole number of at least 5. Restarting all inputs.")
        continue

    try:
        mass = float(input("Car mass (kg; greater than 0): "))
    except ValueError:
        print("Mass must be a finite number greater than 0. Restarting all inputs.")
        continue
    if not np.isfinite(mass) or mass <= 0:
        print("Mass must be a finite number greater than 0. Restarting all inputs.")
        continue

    try:
        speed = float(input("Desired speed at the finish (m/s; greater than 0 and less than 10): "))
    except ValueError:
        print("Final speed must be a finite number greater than 0 and less than 10 m/s. Restarting all inputs.")
        continue
    if not np.isfinite(speed) or speed <= 0 or speed >= 10:
        print("Final speed must be a finite number greater than 0 and less than 10 m/s. Restarting all inputs.")
        continue

    final_height = height - speed**2/(2*g)
    if final_height < 0:
        print("Final height would be below ground. Increase height or decrease speed. Restarting all inputs.")
        continue

    #random widths for the hills between 20% and 85% of the distance
    widths = []
    for n in range(2*(hills - 1)):
        widths.append(np.random.uniform(0.5, 1.5))
    total_width = sum(widths)

    x_points = [0, 0.1 * distance, 0.2 * distance]
    for n in range(2*(hills - 1)):
        x_points.append(x_points[-1] + 0.65 * distance * widths[n]/total_width)
    x_points.append(distance)

    #random peak heights, all below the initial peak
    y_points = [0, height, 0]
    for n in range(hills - 1):
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
print(f"Total hills (including initial peak): {hills}")
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
results = (f"Track length: {length:.2f} m\nTotal hills (including initial peak): {hills}\nMass: {mass:g} kg\n"
           f"Maximum PE: {max_pe/1000:.2f} kJ\nFinal KE: {final_ke/1000:.2f} kJ\n"
           f"Final speed: {final_speed:.2f} m/s")
plt.text(distance, 1.6 * height, results, ha="right", va="top")
plt.tight_layout()

output = Path(__file__).with_name("rollercoaster.png")
plt.savefig(output, dpi=200)
print(f"Plot saved to: {output}")
plt.show()
