import threading
import time

import cv2
import easytello

from localization_module import localization


class Controller:
    def __init__(self):
        self.drone = easytello.Tello()
        self.send_rc(0, 0, 0, 0)
        print("takeoff")
        self.drone.takeoff()
        self.drone.send_command('streamon')
        self.loc = localization.Localization()
        time.sleep(5)
        self.last_error_x = 0
        self.last_error_y = 0
        self.goal_x = None
        self.goal_y = None
        self.control = threading.Thread(target=self.control_thread)
        self.control.start()

    def control_thread(self):
        while self.loc.running:
            x, y = self.goal_x, self.goal_y
            if x is not None and y is not None:
                command, arguments = self.proportional_checking(x, y)
                command(*arguments)
            time.sleep(0.1)

    def proportional_checking(self, x, y):
        """
       Send RC control via four channels.
           a: left/right (-100~100)
           b: forward/backward (-100~100)
           c: up/down (-100~100)
           d: yaw (-100~100)
        """
        KPy = 0.3
        KPf = 0.3

        KDy = 0.1
        KDf = 0.1
        current_x, current_z = self.loc.get_xy()
        error_left = x - current_x
        error_forward = y - current_z

        D_left = error_left - self.last_error_x
        D_forward = error_forward - self.last_error_y

        self.last_error_x = D_left
        self.last_error_y = D_forward

        print(f'Px: {KPy * error_left}, Dx: {KDy * D_left}, Py: {KPf * error_forward}, Dy: {KDf * D_forward}')
        return self.send_rc, (int(KPy * error_left + KDy * D_left), int(KPf * error_forward + KDf * D_forward), 0, 0)

    def send_rc(self, a, b, c, d):
        command = 'rc {} {} {} {}'.format(a, b, c, d)
        #print('Sending command: {}'.format(command))
        self.drone.socket.sendto(command.encode('utf-8'), self.drone.tello_address)