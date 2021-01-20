import threading
import time

import cv2
import easytello

import localization_module.localization as loc


def send_rc(drone, a, b, c, d):
    command = 'rc {} {} {} {}'.format(a, b, c, d)
    print('Sending command: {}'.format(command))
    drone.socket.sendto(command.encode('utf-8'), drone.tello_address)


def proportional_checking(drone, location, x, y):
    """
   Send RC control via four channels.
       a: left/right (-100~100)
       b: forward/backward (-100~100)
       c: up/down (-100~100)
       d: yaw (-100~100)
    """
    KPy = 0.5
    KPf = 0.5
    current_x, current_z = location.get_xy()
    error_left = x - current_x
    error_forward = y - current_z
    return send_rc, (drone, -int(KPy * error_left), int(KPf * error_forward), 0, 0)


def move_to_location(drone, location, x, y):
    command, arguments = proportional_checking(drone, location, x, y)
    command(*arguments)


def drone_init():
    drone = easytello.Tello()
    drone.send_command('streamon')
    print("takeoff")

    drone.takeoff()
    return drone


if __name__ == '__main__':
    drone = drone_init()
    try:
        print("TRYING TO MOVE")
        while loc.location is None:
            continue
        for i in range(1):
            move_to_location(drone, 184, 184)
    except Exception as e:
        loc.running = False
        print("SAD", e)
        drone.land()
    drone.land()
