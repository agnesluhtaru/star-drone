import easytello

if __name__ == '__main__':
    tello = easytello.Tello()
    tello.takeoff()
    tello.go(50, 50, 0, 50)
    tello.land()
