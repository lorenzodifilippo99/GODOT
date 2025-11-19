import numpy as np
import matplotlib.pyplot as plt
from godot.core import num, tempo, events

freq = num.TwoPi
ref_epoch = tempo.Epoch("0.0 TDB")
def f(e):
    t = (e - ref_epoch) / tempo.SecondsInDay
    return t * np.cos(t * freq)

ran = tempo.EpochRange(tempo.Epoch("0.0 TDB"), tempo.Epoch("4.0 TDB")) # 4 days range
grid = ran.createGrid(1e-2 * tempo.SecondsInDay)  # grid with 0.01 DAYS step, N.B. secondsInDay is just a constant (numero di secondi in un giorno)
t = [e.mjd() for e in grid] # transform the grid in mjd values for plotting
x = [f(e) for e in grid] # evaluate the function on the grid

# plot the function over the range 
plt.figure(figsize=(10, 5))
plt.xlabel("Time (day)")
plt.ylabel("Function value (1)")
plt.plot(t, x, label="f")
plt.grid()
plt.legend()
plt.savefig("tutorial_events_1.png")

# now we want to find the roots of the function f over the range defined above
tol = 1e-9
eps = 1e-3
event_grid = ran.createGrid(0.3 * tempo.SecondsInDay) # coarser grid for event detection

ev = events.generateEventSet(f, eps, event_grid, tol) # find the events

event_t = [e.mjd() for e in event_grid] # extract the event grid in mjd format for plotting
event_x = [f(e) for e in event_grid] # evaluate the function on the event grid
roots = [entry.value().mjd() for entry in ev] # extract the root epochs in mjd format

plt.figure(figsize=(10, 5))
plt.xlabel("Time (day)")
plt.ylabel("Function value (1)")
plt.plot(t, x, label="f")
plt.plot(roots, [0] * len(roots), 'o', label="roots")
plt.grid()
plt.legend()
plt.savefig("tutorial_events_2.png")

f_above_zero = events.generateEventIntervalSet(f, eps, event_grid, tol)
for entry in f_above_zero:
    print("starts", entry.start())
    print("ends", entry.end())

f_ranges = [tempo.EpochRange(entry.start().value(), entry.end().value()) for entry in f_above_zero]


plt.figure(figsize=(10, 5))
plt.xlabel("Time (day)")
plt.ylabel("Function value (1)")
plt.plot(t, x, label="f")
for ran in f_ranges:
    grid_ev = ran.createGrid(1e-2 * tempo.SecondsInDay)
    t_ev = [e.mjd() for e in grid_ev]
    x_ev = [f(e) for e in grid_ev]
    plt.plot([ran.start().mjd(), ran.end().mjd()], [0, 0], '-ok', linewidth=3)
    plt.plot(t_ev, x_ev, '-k', linewidth=3)
plt.grid()
plt.legend()
plt.savefig("tutorial_events_3.png")
