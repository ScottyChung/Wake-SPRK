# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 12:30:59 2021

@author: schung
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import wfu_stewart
from controller import Dynamixel
import time

# Slider Update Functions
def update_x(val):
    viewer_pos[0] = val
    update_model()
    
def update_y(val):
    viewer_pos[1] = val
    update_model()    
    
def update_z(val):
    viewer_pos[2] = val
    update_model()   
    
def update_rx(val):
    viewer_rotation[0] = val
    update_model()
    
def update_ry(val):
    viewer_rotation[1] = val
    update_model()
    
def update_rz(val):
    viewer_rotation[2] = val
    update_model()

def update_model():
    
    # Builds rotation matrix 
    viewer_rotation_matrix = R.from_euler('xyz',viewer_rotation,degrees=True).as_matrix()
    
    #Update the models pose
    angles = platform.update_pose(viewer_pos, viewer_rotation_matrix)
    
    if controller:
        #Send angles
        dynamixel.set_all_position(angles)
    
    # Data for three-dimensional scattered points
    p = platform.platformJoints.transpose()
    p = np.concatenate((p,np.ones((1,6))))
    
    p_base = np.matmul(platform.desired_pose, p).transpose()
    zdata = p_base[:,2]
    xdata = p_base[:,0]
    ydata = p_base[:,1]
    top_points._offsets3d = (xdata, ydata, zdata);
    
    verts = [tuple(p) for p in p_base[:,0:3]]
    top_poly.set_verts([verts])
    
    # Data for horns
    zdata = platform.a[:,2]
    xdata = platform.a[:,0]
    ydata = platform.a[:,1]
    horn_points._offsets3d = (xdata,ydata,zdata)
    
    # Drawing legs
    for i,l in enumerate(leg_lines):
        l[0].set_data_3d([platform.a[i,0],p_base[i,0]],
              [platform.a[i,1],p_base[i,1]],
              [platform.a[i,2],p_base[i,2]])
        
    # Drawing horn lines
    for i,l in enumerate(horn_lines):
        l[0].set_data_3d([platform.baseJoints[i,0], platform.a[i,0]],
                  [platform.baseJoints[i,1], platform.a[i,1]],
                  [platform.baseJoints[i,2], platform.a[i,2]])
    plt.draw()
    plt.pause(0.0001)
    
def create_model():
    #Creates
    ax.cla()
    ax.axes.set_xlim3d(left=-150, right=150) 
    ax.axes.set_ylim3d(bottom=-150, top=150) 
    ax.axes.set_zlim3d(bottom=-10, top=250) 
    
    viewer_rotation_matrix = R.from_euler('xyz',viewer_rotation,degrees=True).as_matrix()
    platform.update_pose(viewer_pos, viewer_rotation_matrix)
    # Data for three-dimensional scattered points
    p = platform.platformJoints.transpose()
    p = np.concatenate((p,np.ones((1,6))))
    
    p_base = np.matmul(platform.desired_pose, p).transpose()
    zdata = p_base[:,2]
    xdata = p_base[:,0]
    ydata = p_base[:,1]
    top_points = ax.scatter3D(xdata, ydata, zdata);
    
    verts = [tuple(p) for p in p_base[:,0:3]]
    poly = Poly3DCollection([verts], alpha=0.8)
    ax.add_collection3d(poly)
    
    # Data for three-dimensional scattered points
    zdata = platform.baseJoints[:,2]
    xdata = platform.baseJoints[:,0]
    ydata = platform.baseJoints[:,1]
    bot_points = ax.scatter3D(xdata, ydata, zdata);
    
    # Data for horns
    zdata = platform.a[:,2]
    xdata = platform.a[:,0]
    ydata = platform.a[:,1]
    horn_points = ax.scatter3D(xdata,ydata,zdata)
    
    # Drawing Legs
    leg_lines = []
    for i in range(0,6):
        leg_lines.append(ax.plot3D([platform.a[i,0],p_base[i,0]],
              [platform.a[i,1],p_base[i,1]],
              [platform.a[i,2],p_base[i,2]],
              color='k',
              alpha=0.3))
    
    # Drawing Servo Horns
    horn_lines = []
    for i in range(0,6):
        horn_lines.append(ax.plot3D([platform.baseJoints[i,0], platform.a[i,0]],
                  [platform.baseJoints[i,1], platform.a[i,1]],
                  [platform.baseJoints[i,2], platform.a[i,2]], 
                  color='g',
                  alpha=0.3))
    return top_points, poly, bot_points, horn_points, leg_lines, horn_lines

# Initialize platform model and home position
platform = wfu_stewart.Platform()
viewer_pos = np.array([0,0,0])
viewer_rotation = np.array([0,0,0])

# Create the figure and the line that we will manipulate
fig = plt.figure(figsize=(10,8))
ax = plt.axes(projection='3d')

ax.axes.set_xlim3d(left=-10, right=10) 
ax.axes.set_ylim3d(bottom=-10, top=10) 
ax.axes.set_zlim3d(bottom=-10, top=10)

# Create Model
top_points, top_poly, bot_points, horn_points, leg_lines, horn_lines = create_model()

# Create Controller
controller = False
if controller:
    portName = 'COM5'
    devicesID = [1,2,3,4,5,6]
    dynamixel = Dynamixel(portName, devicesID)
    dynamixel.enable_all_torque()

axcolor = 'lightgoldenrodyellow'
ax.margins(x=0)

# adjust the main plot to make room for the sliders
plt.subplots_adjust(bottom=0.25)

# Make a horizontal slider to control the frequency.
axfreq = plt.axes([0.25, 0.12, 0.65, 0.03], facecolor=axcolor)
x_position = Slider(
    ax=axfreq,
    label='X Position',
    valmin=-50,
    valmax=50,
    valinit=0,
)
axfreq = plt.axes([0.25, 0.07, 0.65, 0.03], facecolor=axcolor)
y_position = Slider(
    ax=axfreq,
    label='Y Position',
    valmin=-50,
    valmax=50,
    valinit=0,
)

axfreq = plt.axes([0.25, 0.02, 0.65, 0.03], facecolor=axcolor)
z_position = Slider(
    ax=axfreq,
    label='Z Position',
    valmin=-50,
    valmax=50,
    valinit=0,
)

axfreq = plt.axes([0.01, 0.12, 0.03, 0.65], facecolor=axcolor)
x_rotation = Slider(
    ax=axfreq,
    label='RX',
    valmin=-50,
    valmax=50,
    valinit=0,
    orientation='vertical',
)

axfreq = plt.axes([0.06, 0.12, 0.03, 0.65], facecolor=axcolor)
y_rotation = Slider(
    ax=axfreq,
    label='RY',
    valmin=-50,
    valmax=50,
    valinit=0,
    orientation='vertical',
)

axfreq = plt.axes([0.11, 0.12, 0.03, 0.65], facecolor=axcolor)
z_rotation = Slider(
    ax=axfreq,
    label='RZ',
    valmin=-50,
    valmax=50,
    valinit=0,
    orientation='vertical',
)

sliders = [x_position,
           y_position,
           z_position,
           x_rotation,
           y_rotation,
           z_rotation]

# register the update function with each slider
x_position.on_changed(update_x)
y_position.on_changed(update_y)
z_position.on_changed(update_z)

x_rotation.on_changed(update_rx)
y_rotation.on_changed(update_ry)
z_rotation.on_changed(update_rz)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = plt.axes([0.8, 0.8, 0.1, 0.04])
resetButton = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    for s in sliders:
        s.reset()

# Attach callback to reset button
resetButton.on_clicked(reset)

def run_trajectory(e):
    times = 3
    t = np.linspace(0,times*2*np.pi,50*times)
    x_list = 30*np.sin(t)
    y_list = 30*np.cos(t)
    for x,y in zip(x_list,y_list):
        #print(x)
        viewer_rotation[0] = x
        viewer_rotation[1] = y
        update_model()
        #time.sleep(.01)
startax = plt.axes([0.8, 0.75, 0.1, 0.04])
startButton = Button(startax, 'Start', color=axcolor, hovercolor='0.975')
startButton.on_clicked(run_trajectory)

# Create a `matplotlib.widgets.Button` to close ports.
closeax = plt.axes([0.8, 0.7, 0.1, 0.04])
closeButton = Button(closeax, 'Quit', color=axcolor, hovercolor='0.975')

def closePort(event):
    dynamixel.close()
    plt.close()
    
closeButton.on_clicked(closePort)