# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 10:22:15 2021

@author: schung

Stewart platform model and visualization
"""

import numpy as np
from scipy.spatial.transform import Rotation as R

class Platform:
        
        def __init__(self,
                     height=181.9,
                     horn_length=60,
                     leg_length=189.7):
            self.initial_height = height
            self.horn_length = horn_length
            self.leg_length = leg_length
            
            #Platform Joint locations
            pJ1 = np.array([-22.5,87.1,0])
            pJ2 = np.array([22.5,87.1,0])
            pJ3 = R.from_euler('z',-120, degrees=True).apply(pJ1)
            pJ4 = R.from_euler('z',-120, degrees=True).apply(pJ2)
            pJ5 = R.from_euler('z',120, degrees=True).apply(pJ1)
            pJ6 = R.from_euler('z',120, degrees=True).apply(pJ2)
            self.platformJoints = np.array([pJ1,pJ2,pJ3,pJ4,pJ5,pJ6])
            
            #Base Joint Locations
            bJ1 = np.array([-34,104,0])
            bJ2 = np.array([34,104,0])
            bJ3 = R.from_euler('z',-120, degrees=True).apply(bJ1)
            bJ4 = R.from_euler('z',-120, degrees=True).apply(bJ2)
            bJ5 = R.from_euler('z',120, degrees=True).apply(bJ1)
            bJ6 = R.from_euler('z',120, degrees=True).apply(bJ2)
            self.baseJoints = np.array([bJ1,bJ2,bJ3,bJ4,bJ5,bJ6])
            
            self.beta = np.array([4*np.pi/3,
                                  -np.pi/3,
                                  2*np.pi/3,
                                  -np.pi,
                                  0,
                                  np.pi/3])
            self.initialize_home()
            
        def initialize_home(self):
            pose = np.eye(4)
            pose[2,3] = self.initial_height
            self.desired_pose = pose
            self.calculate_angles()
            
        def height_offset(self, t):
            #Create new reference
            desired_position = t.copy()
            #Adjust for platform height
            desired_position[2] = t[2] + self.initial_height
            return desired_position
            
        def translate(self, motion):
            '''
            Moves platform to absolute cartesian position

            Parameters
            ----------
            motion : numpy array
                3d point repesenting the position

            Returns
            -------
            numpy array of joint angles
                joint angles to achieve the position.

            '''
            return self.update_pose(translation=motion)
        
        def rotate(self, angles):
            rotation = R.from_euler('xyz',angles,degrees=True).as_matrix()
            return self.update_pose(rotation = rotation)
        
        def update_pose(self,translation=None,rotation=None, euler=None):
            if translation is not None:
                translation = self.height_offset(translation)
                self.desired_pose[0:3,3] = translation
                
            if euler:
                rotation = R.from_euler('xyz',rotation,degrees=True).as_matrix()
            if rotation is not None:
                self.desired_pose[0:3,0:3] = rotation
            
            return self.calculate_angles()
        
        def calculate_angles(self,
                             desired_pose=None):
            if desired_pose is None:
                desired_pose = self.desired_pose
            """Given: desired_pose - 4x4 column transformation matrix"""
            q = self.calculate_q(desired_pose)
            l = q - self.baseJoints
            l_mag = np.linalg.norm(l,axis=1)
            L = l_mag**2-(self.leg_length**2-self.horn_length**2)
            M = 2*self.horn_length*(q[:,2] - self.baseJoints[:,2])
            N = 2*self.horn_length*(np.cos(self.beta) * (q[:,0]-self.baseJoints[:,0]) + \
                                    np.sin(self.beta) * (q[:,1]-self.baseJoints[:,1]))
        
            self.alpha = np.arcsin(L/np.sqrt(M**2+N**2)) - np.arctan(N/M)
            #print(self.alpha)
            if True:
                self.visual_calculations()
                
            return self.alpha
        
        def visual_calculations(self):
            a = []
            for i in range(0,6):
                x = self.horn_length*np.cos(self.alpha[i])*np.cos(self.beta[i]) 
                y = self.horn_length*np.cos(self.alpha[i])*np.sin(self.beta[i]) 
                z = self.horn_length*np.sin(self.alpha[i]) 
                
                point = np.array([x,y,z])+self.baseJoints[i]
                a.append(point)
            self.a = np.array(a)
            
        def calculate_q(self,
                        desired_pose):
            """Platform anchor relative to base CS"""
            q = np.array([np.matmul(desired_pose,np.append(p,1)) for p in self.platformJoints])
            return q[:,0:3]
        
  
