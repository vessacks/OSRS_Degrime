import mouse
import numpy as np
from time import sleep
sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)

def wind_mouse(start_x, start_y, dest_x, dest_y, G_0=8, W_0=3, M_0=15, D_0=12, speed = .5, move_mouse=lambda x,y: None): 
    '''
    WindMouse algorithm. Calls the move_mouse kwarg with each new step.
    Released under the terms of the GPLv3 license.
    G_0 - magnitude of the gravitational fornce. default 9
    W_0 - magnitude of the wind force fluctuations. default 3
    M_0 - maximum step size (velocity clip threshold). default 15
    D_0 - distance where wind behavior changes from random to damped. default 12
    speed - ranges between 0 and 1. it describes the probability of triggering a .02 second delay. I make speed.
    '''
    current_x,current_y = start_x,start_y
    v_x = v_y = W_x = W_y = 0
    while (dist:=np.hypot(dest_x-start_x,dest_y-start_y)) >= 1:
        W_mag = min(W_0, dist)
        if dist >= D_0:
            W_x = W_x/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
            W_y = W_y/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
        else:
            W_x /= sqrt3
            W_y /= sqrt3
            if M_0 < 3:
                M_0 = np.random.random()*3 + 3
            else:
                M_0 /= sqrt5
        v_x += W_x + G_0*(dest_x-start_x)/dist
        v_y += W_y + G_0*(dest_y-start_y)/dist
        v_mag = np.hypot(v_x, v_y)
        if v_mag > M_0:
            v_clip = M_0/2 + np.random.random()*M_0/2
            v_x = (v_x/v_mag) * v_clip
            v_y = (v_y/v_mag) * v_clip
        start_x += v_x
        start_y += v_y
        move_x = int(np.round(start_x))
        move_y = int(np.round(start_y))
        if current_x != move_x or current_y != move_y:
            #This should wait for the mouse polling interval
            #print('x is %s, y is %s' %(move_x,move_y))
            mouse.move(current_x:= move_x,current_y:= move_y,absolute=True)
        if np.random.random() > speed:
            sleep(.02)
    return current_x,current_y

'''
test_start_coords = []
for num in range(10):
    num = num*20
    num = num + 400
    test_start_coords.append(num)
import pyautogui
import time
for num in test_start_coords:
    mouse.move(100,num)
    pyautogui.mouseDown()
    time.sleep(1)
    wind_mouse(100,num,800,num,)
    pyautogui.mouseUp()
    time.sleep(1)
'''

