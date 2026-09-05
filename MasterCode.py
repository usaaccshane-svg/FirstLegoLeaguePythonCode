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
import hub #pyright: ignore[reportMissingImports]
from hub import port # pyright: ignore[reportMissingImports]

print("Library Load Success")
print("Starting Function load")

#You may be asking why should I use the functions, well its because it has checks for reliability and debugging

class MotorFunctions:
    print("Loading Motor Functions")
    @staticmethod
    def  MotorAbsolutePositionCheck(chose_port):
        print(chose_port)
        chose_port_value = motor.absolute_position(chose_port) #Saves Value
        if not (0 <= chose_port_value <359): #Checks for positional errors
            print("Nonsensical value")
            return None
        print(chose_port_value)
        print("Successful")
        return chose_port_value

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
            return result
        else:
            print("Post Check Not On")
            print("Function Ending")
            return None


    @staticmethod
    def MotorVelocityCheck(chose_port):
        print(chose_port)
        motor_velocity = motor.velocity(chose_port)
        print(motor_velocity)
        print("Success")
        return motor_velocity

    @staticmethod
    def MotorHighResolutionCheck(chose_port):
        print("Checking High Resolution")
        high_resolution_status = motor.motor_get_high_resolution_mode(chose_port)
        if high_resolution_status == True:
            print("High Resolution Status True")
            return True
        else:
            print("High Resolution Status False")
            return False

print("MotorFunctions Loaded")

class BatteryFunctions:
    print("Loading Battery Functions")
    
    @staticmethod
    def GetBatteryVoltage(ConversionToVolts): #Boolean 
        current_battery_voltage = hub.battery_voltage()
        print("Battery Voltage Read")
        
        if ConversionToVolts == True:
            print('Converting to Volts')
            ConvertedVoltage = current_battery_voltage/1000
            print(ConvertedVoltage)
            return ConvertedVoltage
        elif ConvertedVoltage == False:
            print(current_battery_voltage)
            return(current_battery_voltage)
        else:
            print("Parameter not true or false")
            return None
    
    @staticmethod
    def GetBatteryTemperature(ConversionMethod): #Type C or F C is for Celsius and F is for Fahrenheit Type N for Kelvin
        print("Getting Battery Temperature")
        current_battery_temp =  hub.battery_temperature()
        
        if ConversionMethod == "N":
            print(current_battery_temp)
            return current_battery_temp
        elif ConversionMethod == "F":
            FahrenheitTemp = (current_battery_temp - 273.15) * 9/5 + 32
            print(FahrenheitTemp)
            return FahrenheitTemp
        elif ConversionMethod == "C":
            CelsiusTemp = current_battery_temp - 273.15
            print(CelsiusTemp)
            return CelsiusTemp
        else:
            print("Unknown Conversion Method Returning None")
            return None
    
    @staticmethod
    def GetBatteryCurrent(ConversionMethod):#True for Amperes leave False for Milliamperes
        print("Getting Battery Current")
        current_battery_current = hub.battery_current()
        if ConversionMethod == False:
            print(current_battery_current)
            return current_battery_current
        elif ConversionMethod == True:
            converted_battery_current = current_battery_current/1000
            print(converted_battery_current)
            return converted_battery_current
        else:
            print("Unknown Conversion Method Returning None")
            return None
    
    @staticmethod
    def GetUsbChargeCurrent(ConversionMethod): #True for Amperes leave false for Milliamperes
        print("Getting USB Charge Current")
        usb_charge_current = hub.usb_charge_current()
        
        if ConversionMethod == False:
            print(usb_charge_current)
            return usb_charge_current
        elif ConversionMethod == True:
            ConvertedUSBChargeCurrent = usb_charge_current/1000
            print(ConvertedUSBChargeCurrent)
            return ConvertedUSBChargeCurrent
        else:
            print("Unknown Conversion Method Returning None")
            return None

print("BatteryFunctions Loaded")
