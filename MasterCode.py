import array as arr
import asyncio
import binascii
import math
import cmath
import collections
import gc
import hashlib
import os
import sys
import time
import motor # pyright: ignore[reportMissingImports]
from hub import port # pyright: ignore[reportMissingImports]

print("Library Load Success")
print("Starting Function load")

#You may be asking why should I use the functions, well its because it has checks for reliability and debugging

class MotorFunctions:
    
    @staticmethod
    def  MotorAbsolutePositionCheck(chose_port):
        print(chose_port)
        chose_port_value = motor.absolute_position(chose_port) #Saves Value
        if not (0 <= chose_port_value <359): #Checks for positional errors
            print("Nonsensical value")
            return None
        print(chose_port_value)
        print("Successful")

    @staticmethod
    def MotorRelativePositionCheck(chose_port):
        print(chose_port)
        chose_port_value = motor.relative_position(chose_port)
        if not isinstance(chose_port_value, int):
            print("Data type not matching")
            print("Returning Null Data")
            return None
        print(chose_port_value)
        print("Successful")
        return chose_port_value

    @staticmethod
    def MotorResetRelativePosition(chose_port, set_position, PostChecks): #set_position is a variable that controls if you want it to set to a specific value. #Post checks is a true and false variables that controls whether you want to make sure that the position reset properly
        print(chose_port)
        print(set_position)
        print(PostChecks)
        motor.reset_relative_position(chose_port, set_position)
        print("Position Reset")
        
        if PostChecks == True:
            result = MotorFunctions.MotorRelativePositionCheck(chose_port)
            print(result)
            print("Success")
        else:
            print("Post Check Not On")
        print("Function Ending")

    @staticmethod
    def MotorVelocityCheck(chose_port):
        print(chose_port)
        motor_velocity = motor.velocity(chose_port)
        print(motor_velocity)
        print("Success")
        return motor_velocity

