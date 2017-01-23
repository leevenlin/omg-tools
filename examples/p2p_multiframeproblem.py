# This file is part of OMG-tools.
#
# OMG-tools -- Optimal Motion Generation-tools
# Copyright (C) 2016 Ruben Van Parys & Tim Mercy, KU Leuven.
# All rights reserved.
#
# OMG-tools is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
import os, sys
sys.path.insert(0,os.getcwd()+'/..')
from omgtools import *

fixed_example = False

# create vehicle
if fixed_example:
    vehicle = Holonomic(shapes = Circle(radius=2), options={'syslimit': 'norm_2'}, bounds={'vmax': 10, 'vmin':-10, 'amax':100, 'amin':-100})
else:
    vehicle = Holonomic(shapes = Circle(radius=0.1), options={'syslimit': 'norm_2'}, bounds={'vmax': 1, 'vmin':-1, 'amax':10, 'amin':-10})

# create environment

if fixed_example:
	##############################################################
	print 'Using environment for known example'
	#for now fix environment to the one for which A*-path is known
	start = [192.546875,32.171875]
	goal = [25.0145107688746,374.855656228109]
	vehicle.set_initial_conditions(start)
	vehicle.set_terminal_conditions(goal)

	envWidth = 300
	envHeight = 400
	distBetween = 40
	environment = Environment(room={'shape': Rectangle(width=envWidth, height=envHeight), 'position': [150, 200], 'draw':True})

	smallSize = 2
	heightObstacles = (envHeight - (4 * distBetween)) / 3.
	widthObstacles = (envWidth/2.) - (2 * distBetween)

	smallRectangle = Rectangle(width=2*smallSize, height=2*smallSize)
	mediumRectangle = Rectangle(width=2*smallSize, height=envHeight/5.-smallSize)
	bigRectangle = Rectangle(width=widthObstacles, height=heightObstacles)

	environment.add_obstacle(Obstacle({'position': [envWidth/2., envHeight/2.]}, shape=smallRectangle))
	environment.add_obstacle(Obstacle({'position': [envWidth/2., distBetween+heightObstacles/2.]}, shape=mediumRectangle))
	environment.add_obstacle(Obstacle({'position': [envWidth/2., distBetween+heightObstacles/2.+2*(distBetween+heightObstacles)]}, shape=mediumRectangle))
	environment.add_obstacle(Obstacle({'position': [distBetween+widthObstacles/2., distBetween+heightObstacles/2.]}, shape=bigRectangle))
	environment.add_obstacle(Obstacle({'position': [distBetween+widthObstacles/2., distBetween+heightObstacles/2.+(distBetween+heightObstacles)]}, shape=bigRectangle))
	environment.add_obstacle(Obstacle({'position': [distBetween+widthObstacles/2., distBetween+heightObstacles/2.+2*(distBetween+heightObstacles)]}, shape=bigRectangle))
	environment.add_obstacle(Obstacle({'position': [distBetween+widthObstacles/2.+envWidth/2., distBetween+heightObstacles/2.]}, shape=bigRectangle))
	environment.add_obstacle(Obstacle({'position': [distBetween+widthObstacles/2.+envWidth/2., distBetween+heightObstacles/2.+(distBetween+heightObstacles)]}, shape=bigRectangle))
	environment.add_obstacle(Obstacle({'position': [distBetween+widthObstacles/2.+envWidth/2., distBetween+heightObstacles/2.+2*(distBetween+heightObstacles)]}, shape=bigRectangle))

	trajectories1 = {'velocity': {'time': [0],
	                             'values': [[-1.5, 0.0]]}}
	trajectories2 = {'velocity': {'time': [0],
	                             'values': [[-1.5, 0.0]]}}
	environment.add_obstacle(Obstacle({'position': [230, 270]}, shape=Rectangle(width=14,height=14), options={'bounce': True},
	                                  simulation={'trajectories': trajectories2}))
	environment.add_obstacle(Obstacle({'position': [150, 210]}, shape=Rectangle(width=14,height=14), options={'bounce': True},
	                                  simulation={'trajectories': trajectories1}))
	################################################################

else:
	# stationary obstacles via GUI
    import Tkinter as tk
    root = tk.Tk()
    options={'cell_size': 0.25}
    gui = EnvironmentGUI(parent=root, width=10, height=10, position=[0,0], options=options)
    root.mainloop()
    environment = gui.getEnvironment()

    # manually add moving obstacles to environment

    # change start and goal
    clicked = gui.getClickedPositions()
    vehicle.set_initial_conditions(clicked[0])
    vehicle.set_terminal_conditions(clicked[1])
    start, goal = clicked[0], clicked[1]

# make global planner
# globalplanner = QuadmapPlanner(environment)
if fixed_example:
	globalplanner = None
    # globalplanner = AStarPlanner(environment, 10, start, goal)
else: 
	globalplanner = AStarPlanner(environment, options['cell_size'], start, goal)

# make coordinator
options={'freeT': True, 'horizon_time': 10, 'fixed_example': fixed_example}
multiproblem=MultiFrameProblem(vehicle, environment, globalplanner, options=options)
multiproblem.set_options({'solver_options': {'ipopt': {'ipopt.linear_solver': 'ma57'}}})
multiproblem.init()

simulator = Simulator(multiproblem)
multiproblem.plot('scene')
vehicle.plot('input', knots=True, prediction=True, labels=['v_x (m/s)', 'v_y (m/s)'])

# run it!
simulator.run()
multiproblem.save_movie('scene', format='gif', name='multiproblemgif', number_of_frames=100, movie_time=5, axis=False)
multiproblem.save_movie('scene', format='tikz', name='multiproblemtikz', number_of_frames=100, movie_time=5, axis=False)