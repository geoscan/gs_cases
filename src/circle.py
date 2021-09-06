#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from gs_flight import FlightController, CallbackEvent
from gs_board import BoardManager
from gs_camera import RunCam
from math import sin, cos, radians
rospy.init_node("circle_node")

print("Enter circle number: ")
circle_num = int(input())
print("Enter circle radius: ")
radius = float(input())

HEIGHT = 2
angle = 0
yaw_current = 0
circle_num_current = 0
run = True
once = False

def new_coord():
    global angle
    global radius
    global circle_num_current

    angle += 1
    if angle > 360:
        angle -= 360
        circle_num_current += 1 
    
    y = radius * sin(radians(angle))
    x = radius * cos(radians(angle)) + radius

    return x, y

def callback(event):
    global ap
    global run
    global circle_num_current
    global circle_num
    global yaw_current
    global camera

    event = event.data
    if event == CallbackEvent.ENGINES_STARTED:
        print("engine started")
        ap.takeoff()
    elif event == CallbackEvent.TAKEOFF_COMPLETE:
        print("takeoff complite")
        ap.updateYaw(yaw_current)
        ap.goToLocalPoint(0,0, HEIGHT)
        camera.power_button() # on recording
    elif event == CallbackEvent.POINT_REACHED:
        if circle_num_current == circle_num:
            camera.power_button() # off recording
            ap.landing()
        else:
            coord = new_coord()
            ap.goToLocalPoint(coord[0], coord[1], HEIGHT)
    elif event == CallbackEvent.POINT_DECELERATION:
        yaw_current -= 1
        if yaw_current > -360:
            yaw_current = 0
        ap.updateYaw(radians(yaw_current))
    elif event == CallbackEvent.COPTER_LANDED:
        print("finish programm")
        run = False

board = BoardManager()
ap = FlightController(callback)
camera = RunCam()

if camera.get_resolution() != "4K@30FPS":
    camera.set_resolution("4K@30FPS")

while not rospy.is_shutdown() and run:
    if board.runStatus() and not once:
        print("start programm")
        ap.preflight()
        once = True

camera.close()