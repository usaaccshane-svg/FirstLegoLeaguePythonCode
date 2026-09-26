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
import color_sensor # pyright: ignore[reportMissingImports]
import color  # pyright: ignore[reportMissingImports]
import device # pyright: ignore[reportMissingImports]


print("Library Load Success")
print("Starting Function load")

wheel_radius = 0.05       # in meters, adjust this value based on your robot's wheel radius
ticks_per_revolution = 360
meter_per_tick = (2 * math.pi * wheel_radius) / ticks_per_revolution



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

update_cycle_time = 10 #Time in milliseconds for how often the data is updated, this is used for the LatestReadings function

current_position = (0,0) #x and y position of the robot in cm, this is used for odometry calculations
x = 0
y = 0

theta = yaw_angle * (math.pi / 180)  # Convert yaw angle to radians

current_ticks_left = motor.relative_position(port.A)
current_ticks_right = motor.relative_position(port.B)

previous_ticks_left = 0
previous_ticks_right = 0

Waypoints = [(0,0),(10,10),(20,20),(30,30)] #List of waypoints for the robot to follow in cm change this to whatever you want, the robot will follow these waypoints in order

async def LatestReadings(): #Helper Process to constantly update data
    global system_status, yaw_angle_vel, pitch_angle_vel, roll_angle_vel, acceleration_values, x_acceleration, y_acceleration, z_acceleration, current_position, Waypoints, update_cycle_time, raw_unfiltered_status, yaw_angle, pitch_angle, roll_angle, theta, previous_ticks_left, previous_ticks_right, current_ticks_left, current_ticks_right, delta_ticks_left, delta_ticks_right,s_left, s_right, d, x, y
    
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
        
        theta = yaw_angle * (math.pi / 180)  # Convert yaw angle to radians
        
        delta_ticks_left = current_ticks_left - previous_ticks_left
        delta_ticks_right = current_ticks_right - previous_ticks_right
        
        previous_ticks_left = current_ticks_left
        previous_ticks_right = current_ticks_right
        
        current_ticks_left = motor.relative_position(port.A)
        current_ticks_right = motor.relative_position(port.B)

        s_left = delta_ticks_left * meter_per_tick
        s_right = delta_ticks_right * meter_per_tick
        
        d=(s_left + s_right) / 2
        
        x += d * math.cos(theta)
        y += d * math.sin(theta)
        current_position = (x, y)
        
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
        print("Delta Ticks Left: ", delta_ticks_left)
        print("Delta Ticks Right: ", delta_ticks_right)
        print("Current Ticks Left: ", current_ticks_left)
        print("Current Ticks Right: ", current_ticks_right)
        print("Previous Ticks Left: ", previous_ticks_left)
        print("Previous Ticks Right: ", previous_ticks_right)
        print("S Left: ", s_left)
        print("S Right: ", s_right)
        print("D: ", d)
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
        if not (0 <= chose_port_value <360): #Checks for positional errors
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
        current_battery_temp =  hub.battery_temperature() # confirm this actually returns Kelvin - if the hub returns Celsius directly, the F/C conversions below will be wrong
        
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
    def Get_Directions_To_Waypoint(waypoint): #Key to Spike Odometry Based Navigational Estimate System or SOBNES for short, this function will calculate the distance and angle to a waypoint from the current position of the robot
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
    async def Go_To_Waypoint(waypoint, base_speed): #Key to Spike Odometry Based Navigational Estimate System or SOBNES for short, this function will move the robot to a waypoint from the current position of the robot
        global current_position
        clockwise = None # This variable will determine the direction of rotation. 0 for clockwise, 1 for counterclockwise
        distance, angle_to_waypoint = CoreFunctions.Get_Directions_To_Waypoint(waypoint)
        print("Moving to Waypoint: ", waypoint)
        print("Distance: ", distance)
        print("Angle: ", angle_to_waypoint)
        
        clockwise = ((angle_to_waypoint * 10) - yaw_angle) % 360
        
        if clockwise <= 179.5:
            print("Turning Clockwise")
            while yaw_angle <= ((angle_to_waypoint * 10)*0.9) - 2 or yaw_angle >= ((angle_to_waypoint * 10)*0.9) + 2:
                motor_pair.move_tank(motor_pair.PAIR_1, base_speed, -base_speed)
                await runloop.sleep_ms(update_cycle_time)
            
            motor_pair.stop(motor_pair.PAIR_1)
            
            while yaw_angle <= ((angle_to_waypoint * 10)) - 1 or yaw_angle >= ((angle_to_waypoint * 10)) + 1:
                            motor_pair.move_tank(motor_pair.PAIR_1, (base_speed*0.2), (-base_speed*0.2))
                            await runloop.sleep_ms(update_cycle_time)
            
            motor_pair.stop(motor_pair.PAIR_1)
            
            
        elif clockwise > 179.5: # widened from >= 180 so the two branches cover every possible value with no gap between them
            print("Turning Counterclockwise")
            while yaw_angle <= ((angle_to_waypoint * 10)*0.9) - 2 or yaw_angle >= ((angle_to_waypoint * 10)*0.9) + 2:
                motor_pair.move_tank(motor_pair.PAIR_1, -base_speed, base_speed)
                await runloop.sleep_ms(update_cycle_time)
            
            motor_pair.stop(motor_pair.PAIR_1)
            
            while yaw_angle <= ((angle_to_waypoint * 10)) - 1 or yaw_angle >= ((angle_to_waypoint * 10)) + 1:
                motor_pair.move_tank(motor_pair.PAIR_1, (-base_speed*0.2), (base_speed*0.2))
                await runloop.sleep_ms(update_cycle_time)
            
            motor_pair.stop(motor_pair.PAIR_1)
            
        else:
            print("Unknown Direction, Stopping")
            motor_pair.stop(motor_pair.PAIR_1)
        
        current_position = waypoint
        print("Arrived at Waypoint: ", current_position)

    @staticmethod
    async def Stop_On_Color_Detection(chose_color,chose_port, base_speed): #This function will stop the robot when it detects a specific color, this is used for color_based navigation and color-based object detection
        while color_sensor.color(chose_port) != chose_color:
            print("Waiting for color:", chose_color)
            print("Current Color: ", color_sensor.color(chose_port))
            motor_pair.move_tank(motor_pair.PAIR_1, base_speed, base_speed)
            await runloop.sleep_ms(update_cycle_time)
        motor_pair.stop(motor_pair.PAIR_1)
    
    @staticmethod
    async def Align_On_line(chose_color,chose_port_left,chose_port_right):
        while color_sensor.color(chose_port_left) != chose_color or color_sensor.color(chose_port_right) != chose_color:
            if color_sensor.color(chose_port_left) != chose_color and color_sensor.color(chose_port_right) == chose_color:
                print("Aligning Left")
                motor_pair.move_tank(motor_pair.PAIR_1, 20, -20)
                await runloop.sleep_ms(update_cycle_time)
            elif color_sensor.color(chose_port_left) == chose_color and color_sensor.color(chose_port_right) != chose_color:
                print("Aligning Right")
                motor_pair.move_tank(motor_pair.PAIR_1, -20, 20)
                await runloop.sleep_ms(update_cycle_time)
            elif color_sensor.color(chose_port_left) != chose_color and color_sensor.color(chose_port_right) != chose_color:
                print("Aligning Both")
                motor_pair.move_tank(motor_pair.PAIR_1, 20, 20)
                await runloop.sleep_ms(update_cycle_time)
        motor_pair.stop(motor_pair.PAIR_1)
        return "Aligned on line"
    
    @staticmethod
    async def Follow_Line(chose_color,chose_port_left,chose_port_right,base_speed): #This function will follow a line based on the color of the line, this is used for line following navigation
        while True:
            if color_sensor.color(chose_port_left) == chose_color and color_sensor.color(chose_port_right) == chose_color:
                print("On Line")
                motor_pair.move_tank(motor_pair.PAIR_1, base_speed, base_speed)
                await runloop.sleep_ms(update_cycle_time)
            elif color_sensor.color(chose_port_left) != chose_color and color_sensor.color(chose_port_right) == chose_color:
                print("Off Line Left")
                motor_pair.move_tank(motor_pair.PAIR_1, base_speed*0.5, base_speed)
                await runloop.sleep_ms(update_cycle_time)
            elif color_sensor.color(chose_port_left) == chose_color and color_sensor.color(chose_port_right) != chose_color:
                print("Off Line Right")
                motor_pair.move_tank(motor_pair.PAIR_1, base_speed, base_speed*0.5)
                await runloop.sleep_ms(update_cycle_time)
            elif color_sensor.color(chose_port_left) != chose_color and color_sensor.color(chose_port_right) != chose_color:
                print("Lost Line")
                motor_pair.stop(motor_pair.PAIR_1)
                break
        return "Line Following Stopped"
    
    @staticmethod
    def Initialize_Robot(): #This function will initialize the robot, this is used for setting up the robot before starting the main function
            global current_position, previous_ticks_left, previous_ticks_right, current_ticks_left, current_ticks_right, system_status,port_A_part, port_B_part, port_C_part, port_D_part, port_E_part, port_F_part,part_list, part_locations
            print("Initializing Robot")
            system_status = True
            current_position = (0,0)
            previous_ticks_left = 0
            previous_ticks_right = 0
            current_ticks_left = motor.relative_position(port.A)
            current_ticks_right = motor.relative_position(port.B)
            
            port_list = [port.A, port.B, port.C, port.D, port.E, port.F]
            motor_port_save = []
            
            for i in range(6):
                if i == 0:
                    port_A = device.id(port.A)
                    port_A_part = 0
                    if port_A == 48:
                        port_A_part = "medium_motor"
                    elif port_A == 49:
                        port_A_part = "large_motor"
                    elif port_A == 61:
                        port_A_part = "color_sensor"
                    elif port_A == 62:
                        port_A_part = "distance_sensor"
                    elif port_A == 63:
                        port_A_part = "force_sensor"
                elif i == 1:
                    port_B = device.id(port.B)
                    port_B_part = 0
                    if port_B == 48:
                        port_B_part = "medium_motor"
                    elif port_B == 49:
                        port_B_part = "large_motor"
                    elif port_B == 61:
                        port_B_part = "color_sensor"
                    elif port_B == 62:
                        port_B_part = "distance_sensor"
                    elif port_B == 63:
                        port_B_part = "force_sensor"
                elif i == 2:
                    port_C = device.id(port.C)
                    port_C_part = 0
                    if port_C == 48:
                        port_C_part = "medium_motor"
                    elif port_C == 49:
                        port_C_part = "large_motor"
                    elif port_C == 61:
                        port_C_part = "color_sensor"
                    elif port_C == 62:
                        port_C_part = "distance_sensor"
                    elif port_C == 63:
                        port_C_part = "force_sensor"
                elif i == 3:
                    port_D = device.id(port.D)
                    port_D_part = 0
                    if port_D == 48:
                        port_D_part = "medium_motor"
                    elif port_D == 49:
                        port_D_part = "large_motor"
                    elif port_D == 61:
                        port_D_part = "color_sensor"
                    elif port_D == 62:
                        port_D_part = "distance_sensor"
                    elif port_D == 63:
                        port_D_part = "force_sensor"
                elif i == 4:
                    port_E = device.id(port.E)
                    port_E_part = 0
                    if port_E == 48:
                        port_E_part = "medium_motor"
                    elif port_E == 49:
                        port_E_part = "large_motor"
                    elif port_E == 61:
                        port_E_part = "color_sensor"
                    elif port_E == 62:
                        port_E_part = "distance_sensor"
                    elif port_E == 63:
                        port_E_part = "force_sensor"
                elif i == 5:
                    port_F = device.id(port.F)
                    port_F_part = 0
                    if port_F == 48:
                        port_F_part = "medium_motor"
                    elif port_F == 49:
                        port_F_part = "large_motor"
                    elif port_F == 61:
                        port_F_part = "color_sensor"
                    elif port_F == 62:
                        port_F_part = "distance_sensor"
                    elif port_F == 63:
                        port_F_part = "force_sensor"
                else:
                    print("Unknown Port, Skipping")
                    continue
            
            part_list = [port_A_part, port_B_part, port_C_part, port_D_part, port_E_part, port_F_part]
            
            print("Checked All Ports")
            print("Port: A: ", port_A_part)
            print("Port: B: ", port_B_part)
            print("Port: C: ", port_C_part)
            print("Port: D: ", port_D_part)
            print("Port: E: ", port_E_part)
            print("Port: F: ", port_F_part)
            

            part_locations = {}
            for i in range(6):
                if part_list[i] in ("medium_motor", "large_motor", "color_sensor", "distance_sensor", "force_sensor"):
                    if part_list[i] not in part_locations:
                        part_locations[part_list[i]] = []
                    part_locations[part_list[i]].append(port_list[i])
            
            print("Part Locations: ", part_locations)
            
            motor_locations = []
            
            for i in range(6):
                if part_list[i] == "medium_motor" or part_list[i] == "large_motor":
                    motor_port_save.append(i)
                    motor_locations.append(port_list[i])
                    print("Motor Found on Port: ", i)
            
            if len(motor_port_save) >= 2:
                motor_pair.pair(motor_pair.PAIR_1, port_list[motor_port_save[0]], port_list[motor_port_save[1]])

            for i in motor_port_save[:4]:
                motor.motor_set_high_resolution_mode(port_list[i], True)
                motor.reset_relative_position(port_list[i], 0)

            print("Motor Locations: ", motor_locations)
            print("Robot Initialized")

print("CoreFunctions Loaded")

async def main(): #Put main code here, this is the main function that will run the robot
    print("Async Main")
    global system_status

    system_status = False #This will stop the LatestReadings function from running, this is used to stop the robot from running when the main function is done

CoreFunctions.Initialize_Robot()
runloop.run(LatestReadings(), main())
