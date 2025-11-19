import godot.core.autodif as ad
import numpy as np
import matplotlib.pyplot as plt


# We can use autodiff in more complex situations. As an example, we define a damped oscillator ODE
# Damped oscillator parameters
k = ad.Scalar(1.0, "k") # spring constant
b = ad.Scalar(0.1, "b") # damping coefficient

# Damped oscillator ODE 
def f(t_, x):
    v = x[1]
    a =  -k * x[0] - b * x[1]
    return ad.concatenate(v, a)

# Runge-Kutte Order 4 stepper
def rk4(t ,x, f, h):
    k1 = f(t, x)
    k2 = f(t + h/2, x + h * k1 / 2)
    k3 = f(t + h/2, x + h * k2 / 2)
    k4 = f(t + h, x + h * k3)
    return x + h * (k1 + k2 + k3 + k4) / 6

# Fixed step size propagation of the oscillator state
def propagate(x0, f, t0, t1, h):
    t = np.arange(t0, t1, h)
    x = [x0]
    for i in t[1:]:
        x.append(rk4(i, x[-1], f, h))
    return t, x

h = 0.1 # step size
x0 = ad.Vector([0, 1], "x0") # initial state with autodiff parameter for initial position

# propagate the state from t=0 to t=100
t, x = propagate(x0, f, 0, 100, h)

# plot the results
plt.rcParams['figure.figsize'] = [12, 6]

def plot(times,state):
    pos = [s[0] for s in state]
    vel = [s[1] for s in state]
    fig, (ax1, ax2) = plt.subplots(1,2)
    ax1.grid()
    ax1.plot(times,[p.value() for p in pos],label='pos')
    ax1.plot(times,[p.value() for p in vel],label='vel')
    ax1.set_xlabel('Time')
    ax1.axhline(0.1, ls='--', lw='1', color='r')
    ax1.axvline(20, ls='--', lw='1', color='r')
    ax1.legend()

    ax2.grid()
    ax2.plot(
        [p.value() for p in pos],
        [p.value() for p in vel]
    )
    ax2.set_xlabel('Pos')
    ax2.set_ylabel('Vel')
    ax2.set_aspect('equal', adjustable='box')
    plt.title("Propagazione con autodiff")
    plt.savefig("./tutorial_propagator_autodiff.png")
plot(t,x)

# compute the gradient of the final position with respect to the initial position
# print the value
x_final = x[-1]
value = x_final.value()
print( f"The value is: \n{value}\n" )

# print the state transition matrix
phi = x_final.at("x0")
print( f"The STM is \n{phi}\n" )

# print the state transition matrix
psi = x_final.at(["k", "b"])
print( f"The STM with respect to parameters k and b is \n{psi}\n" )

# print the full state transition matrix
phi2 = x_final.at(["x0", "k", "b"])
print( f"The full STM is \n{phi2}\n" )
