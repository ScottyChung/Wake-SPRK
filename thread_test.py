# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 14:44:45 2021

@author: schung
"""
import time
import threading

class Viewer():
    isStopped = False
    def __init__(self, anobject):
        self.anobject = anobject
        
    def update_frame(self):
        while not self.isStopped:
            print('Slower UI update')
            print(self.anobject.value)
            time.sleep(1)
        
    def set_stopped(self,val):
        self.isStopped = val
        
class Controller():
    isStopped = False
    def __init__(self, anobject):
        self.anobject = anobject
        
    def send_positions(self):
        while not self.isStopped:
            print('Faster position commands')
            print(self.anobject.value)
            time.sleep(0.1)
            
    
    def set_stopped(self,val):
        self.isStopped = val
        
class Model():
    
    def __init__(self):
        self.value = 0
    def update(self, value):
        self.value = value
        

m = Model()

v = Viewer(m)
c = Controller(m)


t1 = threading.Thread(target=v.update_frame, daemon=True)
t2 = threading.Thread(target=c.send_positions, daemon=True)

#t1.start()
#t2.start()

while True:
    #v.set_stopped(True)
    #c.set_stopped(True)
    pass