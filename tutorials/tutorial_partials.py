# tutorial_partials.py
from godot import cosmos
from godot.core import util
import godot.core.tempo as tempo
import godot.model.common as common
import godot.model.frames as frames

# create the universe
uniConfig = cosmos.util.load_yaml('universe.yml')
uni = cosmos.Universe(uniConfig)

# create the trajectory
traConfig = cosmos.util.load_yaml('trajectory.yml')
tra = cosmos.Trajectory(uni, traConfig)
# avoid verbose propagator logging
util.suppressLogger()

# track all available partials 
uni.parameters.track(uni.parameters.contains())
print(uni.parameters)

# propagate with partials
tra.compute(partials = True)

util.suppressLogger()

class f(common.ScalarTimeEvaluable):
    def __init__(self):
        super().__init__()
        pass
    def eval(self, e):
        return uni.frames.distance('Earth', 'GeoSat_center', e)
    
func = f()
e = tempo.XEpoch("2000-01-01T12:00:00.000 TDB")
d = common.resolve( func.eval(e) )
df_dt_ad = d.at("launch_dt")[0]

print("Distance Earth - GeoSat_center (km): ", d.value())
print("Partial of distance Earth - GeoSat_center with respect to launch time (s): ", df_dt_ad)