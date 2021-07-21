#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# Original Author: Ryu Woon Jung (Leon)
# Edited by: Scotty Chung


import os
from math import pi
import time
from threading import Thread

def getch():
    return os.raw_input()

from dynamixel_sdk import PortHandler,PacketHandler, \
    COMM_SUCCESS, GroupSyncWrite, \
    DXL_LOBYTE, DXL_LOWORD, DXL_HIBYTE, DXL_HIWORD               # Uses Dynamixel SDK library

class Dynamixel(Thread):
    # Control table address
    ADDR_PRO_TORQUE_ENABLE      = 64               # Control table address is different in Dynamixel model
    ADDR_PRO_GOAL_POSITION      = 116
    ADDR_PRO_PRESENT_POSITION   = 132
    ADDR_PROFILE_ACCEL          = 108
    
    # Data Byte Length
    LEN_PRO_GOAL_POSITION       = 4
    LEN_PRO_PRESENT_POSITION    = 4

    # Protocol version
    PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel
    
    # Default setting
    DXL_ID                      = 1                 # Dynamixel ID : 1
    BAUDRATE                    = 57600             # Dynamixel default baudrate : 57600    
    TORQUE_ENABLE               = 1                 # Value for enabling the torque
    TORQUE_DISABLE              = 0                 # Value for disabling the torque
    DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold
    DEG_TO_PULSE = 0.0879
    
    def __init__(self, portName, devicesID):
        '''
        Parameters
        ----------
        portName : STR
            Check which port is being used on your controller
            # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*.
        devicesID : LIST of INT
            ID of motors following the clockwise order.

        Returns
        -------
        None.

        '''
        super().__init__()
        self.running = True
        self.devicesID = devicesID
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(portName)
        
        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)
        
        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()
        
        
        # Set port baudrate
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()
        
        # Initialize GroupSyncWrite instance
        self.groupSyncWrite = GroupSyncWrite(self.portHandler, 
                                             self.packetHandler, 
                                             self.ADDR_PRO_GOAL_POSITION, 
                                             self.LEN_PRO_GOAL_POSITION)
        
    def send_to_all(self, addr, data):
        
         for d in self.devicesID:
            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, 
                                                                             d, 
                                                                             addr, 
                                                                             data)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                print("Dynamixel has been successfully connected")
                      
    
    def enable_all_torque(self):
        for d in self.devicesID:
            self.enable_torque(d)
            
    def enable_torque(self, deviceID):
        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, 
                                                                  deviceID, 
                                                                  self.ADDR_PRO_TORQUE_ENABLE, 
                                                                  self.TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")
    
    def set_all_position(self, angles):
        # Convert angles
        pulses = self._convert_angles(angles)
        #print(pulses)
        # Send to internal command
        self._send_goal_positions(pulses)
        
    def _convert_angles(self,angles):
        # Convert angle to pulse
        pulses = [int(((180/pi)*a)/self.DEG_TO_PULSE) for a in angles]
        pulses[0::2] = [p + 1024 for p in pulses[0::2]] # Odd index motor adjustment
        pulses[1::2] = [-p + 3072 for p in pulses[1::2]] # Even index motor adjustment
        return pulses
    
    def _byte_array(self, val):
        return [DXL_LOBYTE(DXL_LOWORD(val)), 
                DXL_HIBYTE(DXL_LOWORD(val)), 
                DXL_LOBYTE(DXL_HIWORD(val)), 
                DXL_HIBYTE(DXL_HIWORD(val))]
    
    def _send_goal_positions(self, dxl_goal_positions):
        # Allocate goal position value into byte array
        for idx, pos in enumerate(dxl_goal_positions):
            param_goal_position = self._byte_array(pos)
            
            dxl_addparam_result = self.groupSyncWrite.addParam(self.devicesID[idx],
                                                               param_goal_position)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % self.devicesID[idx])
                quit()
                
        # Write goal position
        # Syncwrite goal position
        dxl_comm_result = self.groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
    
        self.groupSyncWrite.clearParam()
    
    def add_model(self, model):
        self.model = model
        
    def read_address(self, address):
         # Read present position
        message, result, error = self.packetHandler.read4ByteTxRx(self.portHandler, 
                                                                  1, 
                                                                  address)
        if result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(result))
        elif error != 0:
            print("%s" % self.packetHandler.getRxPacketError(error))
            
        return message
            
    def run(self):
        #Run at specified rate
        period = 0.01
        t = time.time()
        while self.running:
            t += period
            self.set_all_position(self.model.alpha)
            time.sleep(max(0,t-time.time()))
        #get model angle values
        #send model angle values
    
    def disable_all_torque(self):
        for d in self.devicesID:
            self.disable_torque(d)
            
    def disable_torque(self,deviceID):
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, 
                                                                       deviceID, 
                                                                       self.ADDR_PRO_TORQUE_ENABLE, 
                                                                       self.TORQUE_DISABLE)
                
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            
    def close(self):
        self.running = False
        time.sleep(0.5)
        self.disable_all_torque()
        # Close port
        self.portHandler.closePort()
    
    
