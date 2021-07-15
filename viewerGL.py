# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 15:15:07 2021

@author: schung
"""
from threading import Thread
import time
import numpy as np
from pyqtgraph.opengl import GLScatterPlotItem, GLGridItem, GLLinePlotItem, GLMeshItem

class Viewer(Thread):
    
    def __init__(self, glViewWidget, model):
        super().__init__()
        self.running = True
        
        self.glViewWidget = glViewWidget
        
        # Set viewing distance
        self.glViewWidget.opts['distance'] = 1200
        self.glViewWidget.opts['azimuth'] = -60
        self.glViewWidget.opts['elevation'] = 35
        
        # Add grid item
        g = GLGridItem()
        g.setSize(300,300,1)
        g.setSpacing(50,50,50)
        
        self.glViewWidget.addItem(g)
        
        self.model = model
        
        # Data for three-dimensional scattered points
        p = self.model.platformJoints.transpose()
        p = np.concatenate((p,np.ones((1,6))))
        
        self.platformPoints = np.matmul(self.model.desired_pose, p).transpose()
        self.sp = GLScatterPlotItem(pos=self.platformPoints, color=(0,0,1,1))
        
        self.glViewWidget.addItem(self.sp)
        
        
        # Data for three-dimensional scattered points
        self.bottomPoints = GLScatterPlotItem(pos=self.model.baseJoints, color=(1,1,0,1))
        self.glViewWidget.addItem(self.bottomPoints)
        
        # Data for horns
        self.hornPoints = GLScatterPlotItem(pos=self.model.a, color=(0,1,0,1))
        self.glViewWidget.addItem(self.hornPoints)
        
        # Data for legs
        legPoints = np.array([j for i in zip(self.model.a, self.platformPoints[:,0:3]) for j in i])
        self.legs = GLLinePlotItem(pos=legPoints, color=(1,1,1,0.5), mode='lines')
        self.glViewWidget.addItem(self.legs)
        
        # Data servo horns
        hornPoints = np.array([j for i in zip(self.model.a, self.model.baseJoints) for j in i])
        self.servoHorns = GLLinePlotItem(pos=hornPoints, color=(0,1,0,0.5), mode='lines')
        self.glViewWidget.addItem(self.servoHorns)
        
        # Platform Poly
        self.top_poly = GLMeshItem(vertexes=np.array(self.platformPoints[:,0:3]), 
                                   faces=np.array([[0,1,2],
                                                   [0,2,3],
                                                   [0,3,4],
                                                   [0,4,5]]),
                                   color=(0,0,1,0.5))
        self.top_poly.setGLOptions('additive')
        self.glViewWidget.addItem(self.top_poly)
      
    
    def update(self, angles):
        # Data for three-dimensional scattered points
        p = self.model.platformJoints.transpose()
        p = np.concatenate((p,np.ones((1,6))))
        
        p_base = np.matmul(self.model.desired_pose, p).transpose()
        
        # Platform Points
        self.sp.setData(pos=p_base)
        
        # Base Points
        self.bottomPoints.setData(pos=self.model.baseJoints)
        
        # Horn Points
        self.hornPoints.setData(pos=self.model.a)
        
        # Legs
        self.platformPoints = np.matmul(self.model.desired_pose, p).transpose()
        legPoints = np.array([j for i in zip(self.model.a, self.platformPoints[:,0:3]) for j in i])
        self.legs.setData(pos=legPoints, color=(1,1,1,0.5), antialias=True)
        
        hornPoints = np.array([j for i in zip(self.model.a, self.model.baseJoints) for j in i])
        self.servoHorns.setData(pos=hornPoints, antialias=True)
        
        # Platform Face
        self.top_poly.setMeshData(vertexes=np.array(self.platformPoints[:,0:3]),
                                  faces=np.array([[0,1,2],
                                                   [0,2,3],
                                                   [0,3,4],
                                                   [0,4,5]]))
        
    def run(self):
        #Run at specified rate
        period = 0.05
        t = time.time()
        while self.running:
            t += period
            self.update(self.model.alpha)
            time.sleep(max(0,t-time.time()))
            
    def stop(self):
        self.running = False