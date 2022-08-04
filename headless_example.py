# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 12:56:58 2021

@author: schung
"""

from wfu_stewart import Platform
from dynamixel import Dynamixel

# Replace with your comm name
port_name ='COM5'

# Initial the model
platform = Platform()

# Initialize the dynamixel controller
dynamixel = Dynamixel(port_name, [1,2,3,4,5,6])
dynamixel.add_model(platform)

# Use the platform object functions to move 
input('test')
platform.translate(np.array([5,0,0]))