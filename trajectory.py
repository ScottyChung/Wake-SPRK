# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 12:03:00 2021

@author: schung
"""

from threading import Thread
import numpy as np
import time

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
        command_rate = 50
        
        # Safe to change
        total_time = 5
        
        # leave alone
        t = np.linspace(0,total_time,command_rate*total_time)
        
        z = 15*np.sin((2*np.pi)/2*t)
        
        for idx, step in enumerate(t):
            self.app.zSlider.setValue(z[idx])
            time.sleep(1/command_rate)
            
        # KEEP
        self.callback()