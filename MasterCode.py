import array as arr
import math
import os
import sys
import time
import runloop # pyright: ignore[reportMissingImports]
import motor # pyright: ignore[reportMissingImports]
import hub #pyright: ignore[reportMissingImports]
import motor_pair # pyright: ignore[reportMissingImports]
from hub import light_matrix, motion_sensor, port # pyright: ignore[reportMissingImports]
import color_sensor # pyright: ignore[reportMissingImports]
import color# pyright: ignore[reportMissingImports]
import device # pyright: ignore[reportMissingImports]








print("Library Load Success")
print("Starting Function load")




Waypoints = [(10,10),(20,20),(30,30)] #List of waypoints for the robot to follow in cm change this to whatever you want, the robot will follow these waypoints in order








#You may be asking why should I use the functions, well its because it has checks for reliability and debugging




class MotorFunctions:
    print("Loading Motor Functions")
    @staticmethod
    def MotorAbsolutePositionCheck(chose_port):
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




print("MotorFunctions Loaded")




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
        async def Go_To_Waypoint(waypoint, base_speed):
            global current_position
            distance, angle_to_waypoint = CoreFunctions.Get_Directions_To_Waypoint(waypoint)
            print("Moving to Waypoint: ", waypoint)
            print("Distance: ", distance)
            print("Angle: ", angle_to_waypoint)




            def get_yaw():
                # tilt_angles() returns yaw in decidegrees, range -1795 to 1800.
                return hub.motion_sensor.tilt_angles()[0] / 10




            def normalize(angle):
                # wrap any angle into (-180, 180]
                return ((angle + 180) % 360) - 180




            target_heading = normalize(angle_to_waypoint)




            # Signed shortest angular distance to target: negative means yaw needs to
            # decrease (turn clockwise), positive means yaw needs to increase (turn counterclockwise).
            diff = normalize(target_heading - get_yaw())




            if diff < 0:
                print("Turning Clockwise")
                while normalize(target_heading - get_yaw()) < -2:
                    motor_pair.move_tank(motor_pair.PAIR_1, base_speed, -base_speed)
                    await runloop.sleep_ms(update_cycle_time)




                motor_pair.stop(motor_pair.PAIR_1)




                while normalize(target_heading - get_yaw()) < -1:
                    motor_pair.move_tank(motor_pair.PAIR_1, (base_speed * 0.2), (-base_speed * 0.2))
                    await runloop.sleep_ms(update_cycle_time)




                motor_pair.stop(motor_pair.PAIR_1)




            elif diff > 0:
                print("Turning Counterclockwise")
                while normalize(target_heading - get_yaw()) > 2:
                    motor_pair.move_tank(motor_pair.PAIR_1, -base_speed, base_speed)
                    await runloop.sleep_ms(update_cycle_time)




                motor_pair.stop(motor_pair.PAIR_1)




                while normalize(target_heading - get_yaw()) > 1:
                    motor_pair.move_tank(motor_pair.PAIR_1, (-base_speed * 0.2), (base_speed * 0.2))
                    await runloop.sleep_ms(update_cycle_time)




                motor_pair.stop(motor_pair.PAIR_1)




            else:
                print("Already Facing Waypoint")
                motor_pair.stop(motor_pair.PAIR_1)




            # Fix 5: now that we're facing the waypoint, actually drive to it.
            # current_position is kept live by the concurrently running LatestReadings()
            # task, so we just drive straight until odometry says we're close enough.
            print("Driving Forward to Waypoint")
            distance_tolerance = 2.5# stop once within this many units of the waypoint




            def distance_remaining():
                return math.sqrt((waypoint[0] - current_position[0]) ** 2 + (waypoint[1] - current_position[1]) ** 2)




            while distance_remaining() > distance_tolerance:
                motor_pair.move_tank(motor_pair.PAIR_1, base_speed, base_speed)
                await runloop.sleep_ms(update_cycle_time)




            motor_pair.stop(motor_pair.PAIR_1)
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
            global current_position, previous_ticks_left, previous_ticks_right, current_ticks_left, current_ticks_right, system_status, port_A_part, port_B_part, port_C_part, port_D_part, port_E_part, port_F_part, part_list, part_locations, medium_motor_ports, large_motor_ports, color_sensor_ports, distance_sensor_ports, force_sensor_ports, motor_port_save, motor_locations, raw_unfiltered_status, yaw_angle_vel, pitch_angle_vel, roll_angle_vel, acceleration_values, x_acceleration, y_acceleration, z_acceleration, yaw_angle, pitch_angle, roll_angle, update_cycle_time, theta, x, y, wheel_radius, ticks_per_revolution, meter_per_tick




            print("Initializing Robot")
            system_status = True
            current_position = (0, 0)
            motor.reset_relative_position(port.A, 0)
            motor.reset_relative_position(port.B, 0)
            current_ticks_left = motor.relative_position(port.A)
            current_ticks_right = motor.relative_position(port.B)
            previous_ticks_left = current_ticks_left - current_ticks_left
            previous_ticks_right = current_ticks_right - current_ticks_right
            motion_sensor.reset_yaw(900)
            motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)








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




            wheel_radius = 0.056    # in meters, adjust this value based on your robot's wheel radius
            ticks_per_revolution = 360
            meter_per_tick = (2 * math.pi * wheel_radius) / ticks_per_revolution




            update_cycle_time = 1 #Time in milliseconds for how often the data is updated, this is used for the LatestReadings function








            x = 0
            y = 0




            current_position = (x, y) #x and y position of the robot in cm, this is used for odometry calculations


            divided_yaw = yaw_angle/10




            theta = math.radians(divided_yaw)






        @staticmethod
        async def Turn_To_Heading(target_heading, base_speed):
            coarse_tolerance_deg = 5
            fine_tolerance_deg = 1
            slow_speed = base_speed * 0.2




            def get_yaw_degrees():
                return hub.motion_sensor.tilt_angles()[0] / 10# decidegrees -> degrees




            def normalize(angle):
                return ((angle + 180) % 360) - 180




            diff = normalize(target_heading - get_yaw_degrees())
            turning_clockwise = diff < 0# negative yaw direction = clockwise




            print("Turning", "Clockwise" if turning_clockwise else "Counterclockwise", "to heading:", target_heading)




            while abs(normalize(target_heading - get_yaw_degrees())) > coarse_tolerance_deg:
                speed = -base_speed if turning_clockwise else base_speed
                motor_pair.move_tank(motor_pair.PAIR_1, speed, -speed)
                await runloop.sleep_ms(update_cycle_time)




            motor_pair.stop(motor_pair.PAIR_1)




            while abs(normalize(target_heading - get_yaw_degrees())) > fine_tolerance_deg:
                speed = -slow_speed if turning_clockwise else slow_speed
                motor_pair.move_tank(motor_pair.PAIR_1, speed, -speed)
                await runloop.sleep_ms(update_cycle_time)




            motor_pair.stop(motor_pair.PAIR_1)
            print("Reached heading:", get_yaw_degrees())








print("CoreFunctions Loaded")




async def LatestReadings(): #Helper Process to constantly update data
    global system_status, yaw_angle_vel, pitch_angle_vel, roll_angle_vel, acceleration_values, x_acceleration, y_acceleration, z_acceleration, current_position, Waypoints, update_cycle_time, raw_unfiltered_status, yaw_angle, pitch_angle, roll_angle, theta, previous_ticks_left, previous_ticks_right, current_ticks_left, current_ticks_right, delta_ticks_left, delta_ticks_right,s_left, s_right, d, x, y, current_position_mm




    while system_status == True:
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




        yaw_angle_converted = yaw_angle / 10




        theta = math.radians(yaw_angle_converted)# Convert yaw angle to radians




        current_ticks_left = -(motor.relative_position(port.A))
        current_ticks_right = motor.relative_position(port.B)




        delta_ticks_left = (current_ticks_left - previous_ticks_left)
        delta_ticks_right = (current_ticks_right - previous_ticks_right)




        previous_ticks_left = current_ticks_left
        previous_ticks_right = current_ticks_right




        s_left = delta_ticks_left * meter_per_tick
        s_right = delta_ticks_right * meter_per_tick




        d = (s_left + s_right) / 2




        x += d * math.cos(theta)
        y += d * math.sin(theta)
        current_position = (-x, -y)
        x_position_cm = (x*100) 
        y_position_cm = (y*100)

        divided_by_2_x = x_position_cm/2
        divided_by_2_y = y_position_cm/2

        divided_by_2_x = divided_by_2_x 

        if divided_by_2_y >= -10000:
            divided_by_2_y = divided_by_2_y 
        


        current_position_cm = (divided_by_2_x,divided_by_2_y)
        



        print("X Acceleration: ", x_acceleration)
        print("Y Acceleration: ", y_acceleration)
        print("Z Acceleration: ", z_acceleration)
        print("Yaw Angle: ", yaw_angle_converted)
        print("Pitch Angle: ", pitch_angle)
        print("Roll Angle: ", roll_angle)
        print("Current Ticks Left: ", current_ticks_left)
        print("Current Ticks Right: ", current_ticks_right)
        print("Current Position(cm): ", current_position_cm)
        print("--------------------------------------------------")
        await runloop.sleep_ms(100)




async def main(): #Put main code here, this is the main function that will run the robot
    print("Async Main")
    print("Starting Main")
    global system_status
    await runloop.sleep_ms(1000)
    light_matrix.show_image(light_matrix.IMAGE_CHESSBOARD)
    motor_pair.move_for_degrees(motor_pair.PAIR_1,1500, 0,velocity=200,stop=motor.SMART_BRAKE) 
    print("Moving Forward for 100 cm")
    await runloop.sleep_ms(200000)
    print("Ending!")
    system_status = False #This will stop the LatestReadings function from running, this is used to stop the robot from running when the main function is done




CoreFunctions.Initialize_Robot()
runloop.run(LatestReadings(), main())




#test values for waypoints Waypoints = [(0,50),(50,0),(-50,100),(0,0)]









