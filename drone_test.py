import easytello

if __name__ == '__main__':
    tello = easytello.Tello()
    #tello.takeoff()
    tello.rc_control(0, 0, 0, 0)
    tello.land()
