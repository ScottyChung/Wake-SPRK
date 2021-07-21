# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 12:03:00 2021

@author: schung
"""

from threading import Thread
import numpy as np
import time
import pandas as pd

class Trajectory(Thread):
    
    def __init__(self, app, callback):
        super().__init__()
        self.app = app
        self.callback = callback
         # Don't Chage
        self.command_rate = 100
        self.wave = None
        
    def run(self):
        self.running = True
        if self.wave == 'Sine':
            self.run_sine()
        elif self.wave == 'Square':
            self.run_square()
        else:
            self.run_lung()
            
    def run_lung(self):
        
        ''' Write trajectory here by adjusting the corresponding sliders
        xSlider: X position
        ySlider: Y position
        zSlider: Z position
        xDial: X Rotation
        yDial: Y Rotation
        zDial: Z Rotation
        '''
        
        data = pd.read_csv('lung_trajectory.csv')
        
        for index, row in data.iterrows():
            translation = [row.x,row.y,row.z]
            rotation = [row.rx,row.ry,row.rz]
            self.app.platform.update_pose(translation, rotation,euler=True)
            time.sleep(1/self.command_rate)
            
        # KEEP
        self.callback()
        
    def run_sine(self):
        pose = [0]*6
        period = 1/self.command_rate
        next_t = time.time()
        start_time = time.time()
        while self.running:
            next_t += period
            dt = time.time()-start_time
            motion = self.amp*np.sin((2*np.pi)/self.period*dt)
            pose[self.axis] = motion
            self.app.platform.update_pose(pose[0:3], pose[3:6], euler=True)
            time.sleep(max(0,next_t-time.time()))
            
    def stop(self):
        self.running = False
    