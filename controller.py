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

# Author: Ryu Woon Jung (Leon)

#
# *********     Read and Write Example      *********
#
#
# Available Dynamixel model on this example : All models using Protocol 2.0
# This example is designed for using a Dynamixel PRO 54-200, and an USB2DYNAMIXEL.
# To use another Dynamixel model, such as X series, see their details in E-Manual(emanual.robotis.com) and edit below variables yourself.
# Be sure that Dynamixel PRO properties are already set as %% ID : 1 / Baudnum : 1 (Baudrate : 57600)
#

import os
from math import pi

def getch():
    return os.raw_input()

from dynamixel_sdk import PortHandler,PacketHandler, \
    COMM_SUCCESS, GroupSyncWrite, \
    DXL_LOBYTE, DXL_LOWORD, DXL_HIBYTE, DXL_HIWORD               # Uses Dynamixel SDK library

class Dynamixel():
    # Control table address
    ADDR_PRO_TORQUE_ENABLE      = 64               # Control table address is different in Dynamixel model
    ADDR_PRO_GOAL_POSITION      = 116
    ADDR_PRO_PRESENT_POSITION   = 132
    
    # Protocol version
    PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel
    
    # Default setting
    DXL_ID                      = 1                 # Dynamixel ID : 1
    BAUDRATE                    = 57600             # Dynamixel default baudrate : 57600    
    TORQUE_ENABLE               = 1                 # Value for enabling the torque
    TORQUE_DISABLE              = 0                 # Value for disabling the torque
    DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold
    DEG_TO_PULSE = 0.879
    
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
        # Send to internal command
        self._send_goal_positions(pulses)
        
    def _convert_angles(self,angles):
        # Convert angle to pulse
        pulses = [((180/pi)*a)/self.DEG_TO_PULSE for a in angles]
        pulses[0::2] = pulses[0::2] + 1024 # Odd index motor adjustment
        pulses[1::2] = -pulses[1::2] + 3072 # Even index motor adjustment
        return pulses
    
    def _send_goal_positions(self, dxl_goal_positions):
        # Allocate goal position value into byte array
        for idx, pos in enumerate(dxl_goal_positions):
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(pos)), 
                                   DXL_HIBYTE(DXL_LOWORD(pos)), 
                                   DXL_LOBYTE(DXL_HIWORD(pos)), 
                                   DXL_HIBYTE(DXL_HIWORD(pos))]
            
            dxl_addparam_result = self.groupSyncWrite.addParam(self.devices.ID[idx],
                                                               param_goal_position)
        
        # Write goal position
        # Syncwrite goal position
        dxl_comm_result = self.groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
    
        self.groupSyncWrite.clearParam()
    
    def disable_all_torque(self):
        for d in self.deviceID:
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
        self.disable_all_torque()
        # Close port
        self.portHandler.closePort()
    
    
