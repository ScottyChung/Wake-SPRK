# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 12:56:58 2021

@author: schung
"""

import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication
from pyqtgraph.opengl import GLViewWidget
import numpy as np
from wfu_stewart import Platform
from dynamixel import Dynamixel
from viewerGL import Viewer
from trajectory import Trajectory

class Ui(QtWidgets.QMainWindow):
    ''' Viewer that listens to user input'''
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('ui/wakeSPRK.ui', self) # Load the .ui file
        
        # Replace placeholder widget
        self.GLViewWidget = GLViewWidget(self.openGLWidget.parent())
        self.leftLayout.replaceWidget(self.openGLWidget, self.GLViewWidget)
        
        # Set policy to preferred horizontal and min expanding vertical
        self.GLViewWidget.setSizePolicy(5,3)
        

        
        # Connect sliders
        self.xSlider.valueChanged.connect(self.update_position)
        self.ySlider.valueChanged.connect(self.update_position)
        self.zSlider.valueChanged.connect(self.update_position)
        self.sliders = [self.xSlider,
                        self.ySlider,
                        self.zSlider]
        
        # Connect dials
        self.xDial.valueChanged.connect(self.update_rotation)
        self.yDial.valueChanged.connect(self.update_rotation)
        self.zDial.valueChanged.connect(self.update_rotation)
        self.dials = [self.xDial,
                      self.yDial,
                      self.zDial]
        
        # Connect accel dial
        self.accelDial.valueChanged.connect(self.update_accel)
        
        # Connect button motors
        self.enableBtn.clicked.connect(self.enable_clicked)
        
        # Connect home button
        self.homeBtn.clicked.connect(self.home_clicked)
        
        # Connect trajectory button
        self.runTrajectoryBtn.clicked.connect(self.run_trajectory)
        
        # Set dynamixel to none at start
        self.dynamixel = None
        
        # Initial the model
        self.platform = Platform()
        
        # Start the visualization
        self.viewer = Viewer(self.GLViewWidget, self.platform)
        self.viewer.start()
        
        self.show() # Show the GUI
        
    def update_accel(self):
        self.dynamixel.set_acceleration(self.accelDial.value())
        
    def run_trajectory(self):
        self.disable_user()
        trajectory = Trajectory(self, self.enable_user)
        trajectory.start()
        
    def disable_user(self):
        ui = self.sliders + self.dials
        for w in ui:
            w.setDisabled(True)
            
    def enable_user(self):
        ui = self.sliders + self.dials
        for w in ui:
            w.setDisabled(False)
            
    def home_clicked(self):
        # Block signals on sliders till last call
        widgetList = [self.xSlider, 
                      self.ySlider, 
                      self.zSlider, 
                      self.xDial, 
                      self.yDial, 
                      self.zDial]
        for w in widgetList:
            w.blockSignals(True)
            w.setValue(0)
            w.blockSignals(False)
        self.update_position()
        self.update_rotation()
            
    def update_position(self):
        self.platform.translate(np.array([self.xSlider.value(),
                                         self.ySlider.value(),
                                         self.zSlider.value()]))

    def update_rotation(self):
        self.platform.rotate([self.xDial.value(),
                              self.yDial.value(),
                              self.zDial.value()])
    
    def enable_clicked(self):
        print('clicked')
        if self.dynamixel is None:
            self.create_dynamixel()
            
        self.dynamixel.enable_all_torque()
        self.dynamixel.start()
        
        self.enableBtn.setText('Disable Motors')
        self.enableBtn.clicked.disconnect()
        self.enableBtn.clicked.connect(self.remove_dynamixel)
        
    def create_dynamixel(self):
        self.dynamixel = Dynamixel('COM5', [1,2,3,4,5,6])
        self.dynamixel.add_model(self.platform)
        
    def remove_dynamixel(self):
        self.dynamixel.close()
        self.dynamixel = None
        self.enableBtn.setText('Enable Motors')
        self.enableBtn.clicked.disconnect()
        self.enableBtn.clicked.connect(self.enable_clicked)

app = QApplication(sys.argv)
ui = Ui()
app.exec_()
