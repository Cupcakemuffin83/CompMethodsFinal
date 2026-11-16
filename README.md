# Roller Coaster Final Project

## Setup and running

Requires Python 3, NumPy, and Matplotlib. From the course folder:

```powershell
python -m pip install numpy matplotlib
python Final/final.py
```

Enter all five values when prompted. The program displays a static plot and saves `rollercoaster.png` beside `final.py`, replacing the previous plot.

## Inputs

| Input | Units | Valid values | Example |
|---|---|---|---|
| Horizontal distance | m | Positive | 600 |
| Initial peak height | m | Positive | 30 |
| Number of additional hills | count | Integer, at least 6 | 6 |
| Mass | kg | Positive | 500 |
| Desired final speed | m/s | Strictly between 0 and 10 | 8 |

The final height must be nonnegative. Actual track length must be between 300 and 1200 m. Invalid inputs or track lengths produce an explanation and restart all five prompts. Each new track gets new random hill heights, so its length also varies.

Horizontal distance is the start-to-finish distance along the x-axis. Actual track length follows the curves and is longer.

## Track construction

The initial peak is at 10% of the horizontal distance, followed by a valley at 20%. Additional peaks and valleys alternate through 85%, ending with a valley. Their horizontal section widths are random weights between 0.5 and 1.5, scaled to fill that portion of the track. The remaining distance is the final ascent. Each additional peak is sampled uniformly between zero and the initial peak height, excluding endpoints. Each valley is then sampled between zero and the lower of its two neighbors, excluding endpoints. This keeps every valley below both neighboring peaks while varying its elevation. If the finish is at ground level, the last valley must also be zero. No fixed random seed is used.

For endpoints (x0, y0) and (x1, y1), each piece uses:

```text
y(x) = y0 + (y1-y0)/2 * [1-cos(pi*(x-x0)/(x1-x0))]
```

Each piece meets its neighbors at the same height with zero slope. The green markers show the exact interior peaks and valleys; black and red squares identify the start and finish. The plot is a height profile, not an animation or a time simulation.

## Physics and numerical methods

A powered lift raises the car to the first peak. It is released from rest there. After release, friction and braking are ignored; initial potential energy drives the ride. Use g = 9.81 m/s^2 and ground-level potential energy zero.

```text
Maximum PE = m*g*H
Final height = H - desired_speed^2/(2*g)
Final KE = m*g*(H-final_height)
Calculated final speed = sqrt(2*Final_KE/m)
```

Energy is reported in joules. The endpoint is elevated because a frictionless car must regain most of its initial height to finish slowly. The calculation describes reaching that endpoint; the car is still moving at the requested final speed.

The sampled track uses uniform x-spacing with at least 200 intervals across the shortest section. Interior slopes use central differences; endpoint slopes use forward/backward differences. Track length is calculated by a manually implemented trapezoidal sum of sqrt(1+slope^2) over x.

Mass changes potential and kinetic energy. It cancels out of the speed equation and does not change geometry. The handout requests five inputs affecting the piecewise function; this implementation follows the selected five-input plan, with mass affecting energy instead.

## Example and verification

For inputs 600, 30, 6, 500, and 8:

- Maximum potential energy: 147150.00 J.
- Final kinetic energy: 16000.00 J.
- Final speed: 8.0000 m/s.
- Final height: approximately 26.7380 m.
- Track length, hill heights, valley heights, and section widths vary each run.

Verification covers random hill bounds, joins and zero slopes, energy conservation after release, mass scaling, invalid inputs, rejection of short/long tracks, and length convergence when sampling resolution doubles. The saved example plot is generated from these five inputs.


## Code structure

The script runs from top to bottom like the lab assignments, with no main() function. It uses lists and append(), explicit loops for numerical differentiation and integration, and plt calls for plotting. The section() function contains the equation connecting two track points.
