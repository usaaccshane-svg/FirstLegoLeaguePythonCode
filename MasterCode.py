import array as arr
import math
import os
import sys
import time
import runloop # pyright: ignore[reportMissingImports]
import motor # pyright: ignore[reportMissingImports]
import hub #pyright: ignore[reportMissingImports]
import motor_pair # pyright: ignore[reportMissingImports]
from hub import port # pyright: ignore[reportMissingImports]

print("Library Load Success")
print("Starting Function load")

system_status = True
raw_unfiltered_status = True
ang_vel = hub.motion_sensor.angular_velocity(True)
yaw_angle_vel = ang_vel[0]
pitch_angle_vel = ang_vel[1]
roll_angle_vel = ang_vel[2]

acceleration_values = hub.motion_sensor.acceleration(raw_unfiltered_status)
x_acceleration = acceleration_values[0]
y_acceleration = acceleration_values[1]
z_acceleration = acceleration_values[2]

tilt_values = hub.motion_sensor.tilt_angles()
yaw_angle = tilt_values[0]
pitch_angle = tilt_values[1]
roll_angle = tilt_values[2]

update_cycle_time = 100 #Time in milliseconds for how often the data is updated, this is used for the LatestReadings function

current_position = (0,0) #x and y position of the robot in cm, this is used for odometry calculations

Waypoints = [(0,0),(10,10),(20,20),(30,30)] #List of waypoints for the robot to follow in cm change this to whatever you want, the robot will follow these waypoints in order

async def LatestReadings(): #Helper Process to constantly update data
    global system_status, tilt_angles, yaw_angle_vel, pitch_angle_vel, roll_angle_vel, acceleration_values, x_acceleration, y_acceleration, z_acceleration, current_position, Waypoints, update_cycle_time, raw_unfiltered_status, yaw_angle, pitch_angle, roll_angle
    
    while system_status:
        ang_vel = hub.motion_sensor.angular_velocity(True)
        yaw_angle_vel = ang_vel[0]
        pitch_angle_vel = ang_vel[1]
        roll_angle_vel = ang_vel[2]
        
        acceleration_values = hub.motion_sensor.acceleration(raw_unfiltered_status)
        x_acceleration = acceleration_values[0]
        y_acceleration = acceleration_values[1]
        z_acceleration = acceleration_values[2]
        
        tilt_values = hub.motion_sensor.tilt_angles()
        yaw_angle = tilt_values[0]
        pitch_angle = tilt_values[1]
        roll_angle = tilt_values[2]

        print("Yaw Angle Velocity: ", yaw_angle_vel)
        print("Pitch Angle Velocity: ", pitch_angle_vel)
        print("Roll Angle Velocity: ", roll_angle_vel)
        print("X Acceleration: ", x_acceleration)
        print("Y Acceleration: ", y_acceleration)
        print("Z Acceleration: ", z_acceleration)
        print("Yaw Angle: ", yaw_angle)
        print("Pitch Angle: ", pitch_angle)
        print("Roll Angle: ", roll_angle)
        print("Current Position: ", current_position)
        print("Waypoints: ", Waypoints)
        print("System Status: ", system_status)
        print("Update Cycle Time: ", update_cycle_time)
        print("Raw Unfiltered Status: ", raw_unfiltered_status)
        print("Latest Readings Function Running")
        print("--------------------------------------------------")
        await runloop.sleep_ms(update_cycle_time)

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
        elif ConversionToVolts == False:
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

class CoreFunctions:
    print("Loading Core Functions")
    
    @staticmethod
    def Get_Directions_To_Waypoint(waypoint):
        global current_position
        print("Current Position: ", current_position)
        print("Going to Waypoint: ", waypoint)
        goal_position = waypoint
        # Calculate the distance to the waypoint
        distance = math.sqrt((goal_position[0] - current_position[0]) ** 2 + (goal_position[1] - current_position[1]) ** 2)
        print("Distance to Waypoint: ", distance)
        #Calculate the angle to the waypoint
        angle_to_waypoint = math.degrees(math.atan2(goal_position[1] - current_position[1], goal_position[0] - current_position[0]))
        print("Angle to Waypoint: ", angle_to_waypoint)
        
        return distance, angle_to_waypoint
    
    @staticmethod 
    def Go_To_Waypoint(waypoint, base_speed):
        global current_position
        clockwise = None # This variable will determine the direction of rotation. 0 for clockwise, 1 for counterclockwise
        distance, angle_to_waypoint = CoreFunctions.Get_Directions_To_Waypoint(waypoint)
        print("Moving to Waypoint: ", waypoint)
        print("Distance: ", distance)
        print("Angle: ", angle_to_waypoint)
        
        clockwise = ((angle_to_waypoint * 10) - yaw_angle) % 360
        
        if clockwise <= 179.5:
            print("Turning Clockwise")
            while yaw_angle <= (angle_to_waypoint * 10) - 2 or yaw_angle >= (angle_to_waypoint * 10) + 2:
                motor_pair.move_tank(motor_pair.PAIR_1, base_speed, -base_speed)
        elif clockwise >= 180:
            print("Turning Counterclockwise")
            while yaw_angle <= (angle_to_waypoint * 10) - 2 or yaw_angle >= (angle_to_waypoint * 10) + 2:
                motor_pair.move_tank(motor_pair.PAIR_1, -base_speed, base_speed)
        else:
            print("Unknown Direction, Stopping")
            motor_pair.stop(motor_pair.PAIR_1)
        
        current_position = waypoint
        print("Arrived at Waypoint: ", current_position)

print("CoreFunctions Loaded")

runloop.run(LatestReadings()) 

async def main(): #Put main code here, this is the main function that will run the robot
    print("Async Main")
    system_status = False #This will stop the LatestReadings function from running, this is used to stop the robot from running when the main function is done

runloop.run(main())
