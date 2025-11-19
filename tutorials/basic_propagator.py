from godot import cosmos
from godot.model import prop
from godot.model import common
from godot.model import interface
from godot.model import geometry
from godot.core.autodif import bridge as br
from godot.core import autodif as ad
from godot.core import tempo, util, constants, integ, astro
import numpy as np
#util.suppressLogger()

# Get frames object and variables for points to use
uni_config = cosmos.util.load_yaml('universe.yml')
uni = cosmos.Universe(uni_config)
fra = uni.frames
icrf = fra.axesId('ICRF')
earth = fra.pointId('Earth')

# Create point for spacecraft
try:
    ChaserPoint = fra.addPoint('Chaser', tempo.TimeScale.TDB)
except:
    ChaserPoint = fra.pointId('Chaser')
try:
    TargetPoint = fra.addPoint('Target', tempo.TimeScale.TDB)
except:
    TargetPoint = fra.pointId('Target')


# Create propagators for both spacecraft
propChaser = prop.PropagatorPoint(fra, icrf, ChaserPoint)
propTarget = prop.PropagatorPoint(fra, icrf, TargetPoint)

# Define epochs
epoch0 = tempo.Epoch("2025-10-29T00:00:00.000 TDB")
epoch1 = tempo.Epoch("2025-10-29T01:00:00.000 TDB")

# Define initial states in Cartesian coordinates
Chaser_coe = ad.Vector6([7000.0, 0.001, 98.0*np.pi/180, 0, 0, 0]) # a,e,i,Ω,ω,ν
Chaser_state0  = astro.cartFromKep(Chaser_coe, constants.EarthEllipsoidGM)

Target_coe = ad.Vector6([7000.0, 0.001, 98.0*np.pi/180, 0, 0, 0]) # a,e,i,Ω,ω,ν
Target_state0  = astro.cartFromKep(Target_coe, constants.EarthEllipsoidGM)

dyn = uni.dynamics.get("solarSystem")
fra.setAlias(dyn.point, ChaserPoint)
fra.setAlias(dyn.point, TargetPoint)
fra.setAlias(dyn.coi, earth)
fra.setAlias(dyn.axes, icrf)
for key, alias in dyn.inputs.items():
    alias.set(uni.parameters.get("{}_{}".format("Spacecraft", key)))

tol = np.full(6, 1e-12)

print('dyn.acc is', dyn.acc)

Chaser_inp = [prop.PointInput(ChaserPoint, earth, Chaser_state0,common.Vector3TimeEvaluable(dyn.acc), tol, tol)]
Target_inp = [prop.PointInput(TargetPoint, earth, Target_state0, dyn.acc, tol, tol)]

# Propaga entrambi separatamente
#Chaser_state = prop.Propagator()

# Define dynamics model

