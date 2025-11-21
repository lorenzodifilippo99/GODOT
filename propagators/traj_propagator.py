from godot import cosmos
from godot.model import geometry
from godot.core import tempo, util, events, constants, integ
import numpy as np
import godot.cosmos.show
from godot.cosmos.show import FramePoint
import os
import time
from tqdm import tqdm
from datetime import datetime

util.suppressLogger()

ImageGeneration = False
N = 30000

# Generate log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs/run_{timestamp}.txt"
log_file = open(log_filename, "w")

if ImageGeneration:
    figures_folder = f"figures/run_{timestamp}"
    os.makedirs(figures_folder, exist_ok=True)

# Nominal initial states
chaser_x0 = 6378.0 + 525.0 # km valore nominale
chaser_y0 = 0.0        # km
chaser_z0 = 0.0        # km     
chaser_vx0 = 0.0       # km/s
chaser_vy0 = 7.5       # km/s
chaser_vz0 = 0.0       # km/s

deltax = 0.0 # distanza nominale lungo x
deltay = 0.010
deltaz = 0.0

threshold = 0.001 # km

target_x0 = chaser_x0 + deltax # km 
target_y0 = chaser_y0 + deltay # km
target_z0 = chaser_z0 + deltaz # km     
target_vx0 = 0.0 # km/s
target_vy0 = 7.5 # km/s
target_vz0 = 0.0 # km/s

# Uncertainties
sigma_chaser_x0 = 0.001    # km incertezza (1 sigma)
sigma_chaser_y0 = 0.001
sigma_chaser_z0 = 0.001
sigma_chaser_vx0 = 3e-6    # km/s incertezza (1 sigma)
sigma_chaser_vy0 = 3e-6
sigma_chaser_vz0 = 3e-6

sigma_target_x0 = 0.0    # km incertezza (1 sigma)
sigma_target_y0 = 0.0
sigma_target_z0 = 0.0
sigma_target_vx0 = 0.0 #3e-6    # km/s incertezza (1 sigma)
sigma_target_vy0 = 0.0 #3e-6
sigma_target_vz0 = 0.0 #3e-6

# Generate N random inital states for both spacecrafts
chaser_initial_pos_x = np.random.normal(loc=chaser_x0, scale=sigma_chaser_x0, size=N)
chaser_initial_pos_y = np.random.normal(loc=chaser_y0, scale=sigma_chaser_y0, size=N)
chaser_initial_pos_z = np.random.normal(loc=chaser_z0, scale=sigma_chaser_z0, size=N)
chaser_initial_vel_x = np.random.normal(loc=chaser_vx0, scale=sigma_chaser_vx0, size=N)
chaser_initial_vel_y = np.random.normal(loc=chaser_vy0, scale=sigma_chaser_vy0, size=N)
chaser_initial_vel_z= np.random.normal(loc=chaser_vz0, scale=sigma_chaser_vz0, size=N)

target_initial_pos_x = np.random.normal(loc=target_x0, scale=sigma_target_x0, size=N)
target_initial_pos_y = np.random.normal(loc=target_y0, scale=sigma_target_y0, size=N)
target_initial_pos_z = np.random.normal(loc=target_z0, scale=sigma_target_z0, size=N)
target_initial_vel_x = np.random.normal(loc=target_vx0, scale=sigma_target_vx0, size=N)
target_initial_vel_y = np.random.normal(loc=target_vy0, scale=sigma_target_vy0, size=N)
target_initial_vel_z= np.random.normal(loc=target_vz0, scale=sigma_target_vz0, size=N)

# Configure Universe and Trajectory
uni_config = cosmos.util.load_yaml('universe.yml')
uni = cosmos.Universe(uni_config)

tra_config_chaser = cosmos.util.load_yaml('trajectory_chaser.yml')
tra_chaser = cosmos.Trajectory(uni, tra_config_chaser)

tra_config_target = cosmos.util.load_yaml('trajectory_target.yml')
tra_target = cosmos.Trajectory(uni, tra_config_target)

# Estremi di propagazione
start_prop = "2027-01-01T00:00:00.000 TDB"
end_prop = "2027-01-01T12:00:00.000 TDB"

duration = tempo.EpochRange(tempo.Epoch(start_prop), tempo.Epoch(end_prop))
dt = duration.width()
uni.parameters.setPhysical('end_dt', dt)
uni.parameters.setPhysical('End_dt', dt)

# Loop per la propagazione e EventDetection
pbar = tqdm(range(N), desc="Monte Carlo", unit="run")

# Definizione evento impatto
def ImpactEvent(epo):
    x = geometry.Range(uni.frames, "chaser_center", "target_center")
    return threshold - x.eval(epo)

impact_counter = 0

for i in pbar:
    t_start = time.time()

    # Set randomized parameters for the chaser
    uni.parameters.setPhysical('InitialPos_chaser_center_pos_x', chaser_initial_pos_x[i])
    uni.parameters.setPhysical('InitialPos_chaser_center_pos_y', chaser_initial_pos_y[i])
    uni.parameters.setPhysical('InitialPos_chaser_center_pos_z', chaser_initial_pos_z[i])
    uni.parameters.setPhysical('InitialPos_chaser_center_vel_x', chaser_initial_vel_x[i])
    uni.parameters.setPhysical('InitialPos_chaser_center_vel_y', chaser_initial_vel_y[i])
    uni.parameters.setPhysical('InitialPos_chaser_center_vel_z', chaser_initial_vel_z[i])

    # Set randomized parameters for the target
    uni.parameters.setPhysical('InitialState_target_center_pos_x', target_initial_pos_x[i])
    uni.parameters.setPhysical('InitialState_target_center_pos_y', target_initial_pos_y[i])
    uni.parameters.setPhysical('InitialState_target_center_pos_z', target_initial_pos_z[i])
    uni.parameters.setPhysical('InitialState_target_center_vel_x', target_initial_vel_x[i])
    uni.parameters.setPhysical('InitialState_target_center_vel_y', target_initial_vel_y[i])
    uni.parameters.setPhysical('InitialState_target_center_vel_z', target_initial_vel_z[i])
    log_file.write(f'\nIteration {i}\n')

    # Propagate orbits
    if not ImageGeneration:
        tra_chaser.compute(False)
        tra_target.compute(False)

    else:
        # Plot the relative position between the two spacecrafts in the ICRF frame
        ax = godot.cosmos.show.Axes(
        projection=(godot.cosmos.show.Dimension.SPACE, godot.cosmos.show.Dimension.SPACE),
        uni=uni,
        origin='target_center',
        axes="ICRF",
        )
        ax.plot(
            tra_target, 
            label="Target Center", 
            start=start_prop,
            end=end_prop,
            color='black',
            add_timeline_legend=False
        )
        ax.plot(
            tra_chaser, 
            label="Chaser Center",
            start=start_prop, 
            end=end_prop, 
            color='black', 
            add_timeline_legend=False
        )
        ax.configure_axes(
            leg_outside=True, 
            aspect='auto', 
            adjustable='datalim'
        )
        ax.savefig(f"{figures_folder}/relative_pos_{i:03d}.png")

        # Plot the position of the two spacecrafts in the Earth-centered ICRF frame    
        # ax2 = godot.cosmos.show.Axes(
        #     projection=(godot.cosmos.show.Dimension.SPACE, godot.cosmos.show.Dimension.SPACE),
        #     uni=uni,
        #     origin="Earth",
        #     axes="ICRF",
        # )
        # ax2.plot(godot.cosmos.show.FramePoint("Earth"), label="Earth", start=start_prop, end=end_prop,)
        # ax2.plot(tra_chaser, start=start_prop, end=end_prop, step=100, color='red', lw=0.5, add_timeline_legend=True)
        # ax2.plot(tra_target, start=start_prop, end=end_prop, step=100, color='black', lw=0.5, add_timeline_legend=True)
        # ax2.configure_axes(leg_outside=True, aspect='auto', adjustable='datalim')
        # ax2.savefig(f"figures/Earth_cent_poss_{i:03d}.png")

        # Plot the distance between the two spacecrafts highlighting the epoch when the distane is below the threshold
        ax3 = godot.cosmos.show.Axes(
            projection=(godot.cosmos.show.Dimension.TIME, godot.cosmos.show.Dimension.SCALAR)
        )
        ax3.plot(godot.model.geometry.Range(uni.frames, "chaser_center","target_center"),label='|chaser-target|', start=start_prop, end=end_prop, step=1)
        ax3.configure_axes(
            dateformat="Calendar_Date",
            ylabel="Distance [km]",
            leg_outside=False,
            leg_loc="best",
        )
        
    tol = 1e-9
    eps = 1e-9
    event_grid = duration.createGrid(100) # grid for event detection
    possible_impact_event = events.generateEventIntervalSet(ImpactEvent, eps, event_grid, tol)

    if len(possible_impact_event):
        impact_counter += 1
        for entry in possible_impact_event:
            log_file.write(f"\t starts {entry.start()}\n")
            log_file.write(f"\t ends {entry.end()}\n")

    if ImageGeneration:
        impact_intervals = [tempo.EpochRange(entry.start().value(), entry.end().value()) for entry in possible_impact_event]
        for interval in impact_intervals:
            ax3.plot(
                geometry.Range(uni.frames, "chaser_center","target_center"), 
                start=interval.start().value(), 
                end=interval.end().value(), 
                color='red', 
                lw=1, 
                step=1
            )     
        ax3.savefig(f"{figures_folder}/Distances_{i:03d}.png")

    if i > 0 and i % 1000 == 0:
        print(' Impact probability after', i, 'iterations:', impact_counter/N)    
        log_file.write(f"Impact probability after {i} simulations: {impact_counter/N}")

    elapsed = time.time() - t_start
    pbar.set_postfix({"last_elapsed": f"{elapsed:.2f}s"})

probability_impact = impact_counter/N

print('\nProbability of unintentional contact over', N, 'simulations:', probability_impact)
print(f"Simulation data: \n \t Time of propagation = {dt/3600} h \n \t Target initial state: {target_x0:.3f} km , {target_y0:.3f} km, {target_z0:.3f} km, {target_vx0*10**3:.3f} m/s, {target_vy0*10**3:.3f} m/s, {target_vz0*10**3:.3f} m/s" )
print(f"\t Chaser initial state: {chaser_x0:.3f} km , {chaser_y0:.3f} km, {chaser_z0:.3f} km, {chaser_vx0*10**6} mm/s, {chaser_vy0*10**6} mm/s, {chaser_vz0*10**6} mm/s" )
print(f"\t Threshold for impact: {threshold*10**3} m")

log_file.write(f'\nProbability of unintentional contact over {N} simulations: {probability_impact}\n')
log_file.write(f"Simulation data: \n \t Time of propagation = {dt/3600} h \n \t Target initial state: {target_x0:.3f} km , {target_y0:.3f} km, {target_z0:.3f} km, {target_vx0*10**3:.3f} m/s, {target_vy0*10**3:.3f} m/s, {target_vz0*10**3:.3f} m/s \n" )
log_file.write(f" \t Chaser initial state: {chaser_x0:.3f} km , {chaser_y0:.3f} km, {chaser_z0:.3f} km, {chaser_vx0*10**6} mm/s, {chaser_vy0*10**6} mm/s, {chaser_vz0*10**6} mm/s \n" )
log_file.write(f" \t Threshold for impact: {threshold*10**3} m")