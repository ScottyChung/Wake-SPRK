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
        
    def run(self):
        
        ''' Write trajectory here by adjusting the corresponding sliders
        xSlider: X position
        ySlider: Y position
        zSlider: Z position
        xDial: X Rotation
        yDial: Y Rotation
        zDial: Z Rotation
        '''
        
        # Don't Chage
        command_rate = 100
        
        data = pd.read_csv('lung_trajectory.csv')
        
        for index, row in data.iterrows():
            translation = [row.x,row.y,row.z]
            rotation = [row.rx,row.ry,row.rz]
            self.app.platform.update_pose(translation, rotation,euler=True)
            time.sleep(1/command_rate)
            
        # KEEP
        self.callback()