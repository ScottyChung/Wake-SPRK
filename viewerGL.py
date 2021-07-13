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
        
        self.top_poly = GLMeshItem(verts=self.platformPoints)
        self.glViewWidget.addItem(self.top_poly)
        '''
        pos = np.random.random(size=(100000,3))
        pos *= [10,-10,10]
        pos[0] = (0,0,0)
        color = np.ones((pos.shape[0], 4))
        d2 = (pos**2).sum(axis=1)**0.5
        size = np.random.random(size=pos.shape[0])*10
        sp2 = gl.GLScatterPlotItem(pos=pos, color=(1,1,1,1), size=size)
        phase = 0.
        
        w.addItem(sp2)
        
        
        verts = [tuple(p) for p in p_base[:,0:3]]
        poly = Poly3DCollection([verts], alpha=0.8)
        ax.add_collection3d(poly)
        
        
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
    '''
    
    def update(self, angles):
        # Data for three-dimensional scattered points
        p = self.model.platformJoints.transpose()
        p = np.concatenate((p,np.ones((1,6))))
        
        p_base = np.matmul(self.model.desired_pose, p).transpose()
        self.sp.setData(pos=p_base)
        
        # Base Points
        self.bottomPoints.setData(pos=self.model.baseJoints)
        
        # Horn Points
        self.hornPoints.setData(pos=self.model.a)
        
        # Legs
        self.platformPoints = np.matmul(self.model.desired_pose, p).transpose()
        legPoints = np.array([j for i in zip(self.model.a, self.platformPoints[:,0:3]) for j in i])
        self.legs.setData(pos=legPoints, color=(1,1,1,0.5), antialias=True)
        '''
        verts = [tuple(p) for p in p_base[:,0:3]]
        top_poly.set_verts([verts])
        
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
        return [top_points]
        '''
        
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