#program to read controlling computer input which will be sent to the Pi

import pygame, sys, time
from pygame.locals import *

import socket, pickle
import random as rand
###
HOST = ''                 # Symbolic name meaning the local host
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)
s.bind((HOST, PORT))
s.listen(5)
###
size = width, height = (500, 500)
current_pos = (width/2.0,height/2.0)
background = (255,255,255)

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pi Communications")
screen.fill(background)

point = pygame.image.load("point.bmp")
pointrect = point.get_rect(center = current_pos)

clock = pygame.time.Clock()

conctd = False
while not conctd:
    conctd = True
    try:
        conn, addr = s.accept()
    except BlockingIOError:
        conctd = False
#################################
def end_program(conn):
    #shutdown procedures
    conn.send(pickle.dumps("halt", protocol=2))
    time.sleep(1)#wait for data to be sent
    conn.close()
    print("Connection closed")
    pygame.quit()
    sys.exit()
#################################
while 1:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_program(conn)

    keys = pygame.key.get_pressed()

#Read keyboard
    ##drivetrain
    drive = 0#forward:1 #back:2 #left:3 #right:4
    move = [0,0]
    if keys[K_UP]:
        move[1] = -1
        drive = 1
    elif keys[K_DOWN]:
        move[1] = 1
        drive = 2
    elif keys[K_LEFT]:
        move[0] = -1
        drive = 3
    elif keys[K_RIGHT]:
        move[0] = 1
        drive = 4
    ##base #right:1 #left:2
    base = 0
    if keys[K_a]:
        base = 2
    elif keys[K_d]:
        base = 1
    ##shoulder #forward:1 #backward:2
    shoulder = 0
    if keys[K_w]:
        shoulder = 1
    elif keys[K_s]:
        shoulder = 2
    ##elbow #up:1 #down:2
    elbow = 0
    if keys[K_r]:
        elbow = 1
    elif keys[K_f]:
        elbow = 2
    ##wrist #up:1 #down:2
    wrist = 0
    if keys[K_t]:
        wrist = 1
    elif keys[K_g]:
        wrist = 2
    ##wrist rotation #left:1 #right:2
    wrist_rotate = 0
    if keys[K_q]:
        wrist_rotate = 1
    elif keys[K_e]:
        wrist_rotate = 2
    ##gripper
    gripper = 0#open:1 #close:2    
    if keys[K_PERIOD]:
        gripper = 1
    elif keys[K_COMMA]:
        gripper = 2
    ##go to home position
    home = 0
    if keys[K_SPACE]:
        home = 1
        
    pointrect = pointrect.move(move)

    ##Send data
    commands = [drive, base, shoulder,
                elbow, wrist, wrist_rotate,
                gripper, home]#values for the robot
    d_to_send = commands
    try:
        conn.send(pickle.dumps(d_to_send, protocol=2))
    except (ConnectionResetError, ConnectionAbortedError):
        print("Client Lost Connection: Trying to reconnect")
        conctd = False
        while not conctd:
            conctd = True
            try:
                conn, addr = s.accept()
            except BlockingIOError:
                conctd = False
        print("Reconnecting successful!")
    ##Receive data
    gripper_sensor=0
    print("sent ",commands, end=" ")
    try:
        data = pickle.loads(conn.recv(1024))
        print("--Reply from client: ", data)
        if data == 1:
            screen.fill((134,12,123))
        else: screen.fill(background)
    except:
        print("--Failed")

    ##draw screen
    screen.blit(point, pointrect)
    pygame.display.flip()
