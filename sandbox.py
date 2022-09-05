# NZM melee

from msilib.schema import Feature
import cv2 as cv
from cv2 import threshold
from cv2 import _InputArray_STD_BOOL_VECTOR
import numpy as np
import os
from windmouse import wind_mouse
from windowcapture import WindowCapture
from vision import Vision
import pyautogui
from pyHM import Mouse
import time
from action import Action

#notes:
# 1. run in classic fixed
# 2. it searches partly in color. don't throw black and white code in willy nilly
# 3. prayer hotkey set to f5 (standard)
# 4. inventory hotkey set to f1 (NOT STANDARD)
# 5. you have to enter the dream and rock down to 1hp before starting the program. 
# 5.1 don't take any overloads! it will do that for you, and if you do it will mess up the timing and observation
# 6. you must also eat 5m of sorbs before starting 
# 7. game chat must be on so it can see the max_sorb message
# 8. don't change inv. /prayer tabs while it's running. it will get confused and give up. 
# 9. don't have anything typed in your chatbox/drafting window. it will mess up the overload_off and max_sorb checks. 
# 10. set new KNOWN_OFFSCREEN_POINT

#thoughts
# 1. consider adding an auto-guzzle every 5 mins or so. if your flicker makes mistakes this will take you back donw to 1hp reliably. 
# 2. consider adding a thing to notice when it's out of prayer and stop flicking. 
# 3. potentially add a pray potting module as well
# 4. USEFUL: instead of timing the overloads off of 51hp (which can go wrong if your flicks screw up), time it off the overload-wearing-off chat message, as with the absorbtion repot. 
input('make sure you have complied with the run notes. then press enter to begin setup...')
print('Click into game. you have 10 seconds...')
time.sleep(2)
print('Click into game. you have 8 seconds...')
time.sleep(2)
print('Click into game. you have 6 seconds...')
time.sleep(2)
print('Click into game. you have 4 seconds...')
time.sleep(2)
print('Click into game. you have 2 seconds...')
time.sleep(2)
print('we are setting up parameters and taking first values. this relies on hotkeys and may fail perniciously if you are not clicked into game ...')
time.sleep(2)


# initialize the WindowCapture class
wincap = WindowCapture('RuneLite - Vessacks')


# initialize the Vision class
#do these color
rapid_heal_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\rapid_heal.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
protect_melee_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\protect_melee.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
protect_melee_on_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\protect_melee_on.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)

#do these grayscale
sorb_one_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_one.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
sorb_two_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_two.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
sorb_three_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_three.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
sorb_four_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_four.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)

#color
max_sorb_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\max_sorb.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
overload_off_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\overload_off.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)
#color
prayer_open_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\prayer_open.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR)

zero_prayer_vision_mask = cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\0_prayer_vision_mask.png', cv.IMREAD_COLOR)
zero_prayer_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\0_prayer.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR, search_mask = zero_prayer_vision_mask)

#do these grayscale
overload_one_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\overload_one.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
overload_two_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\overload_two.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
overload_three_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\overload_three.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
overload_four_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\overload_four.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)

#do these grayscale
praypot_one_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\praypot_one.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
praypot_two_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\praypot_two.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
praypot_three_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\praypot_three.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
praypot_four_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\praypot_four.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)

#overload_active_vision = #I dont' think I use this

#color and mask
fifty_one_health_vision_mask= cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\51_hp_vision_mask.png', cv.IMREAD_COLOR)
fifty_one_health_vision= Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\51_hp.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR, search_mask=fifty_one_health_vision_mask)

one_health_vision_mask = cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\1_hp_vision_mask.png', cv.IMREAD_COLOR)
one_health_vision= Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\1_hp.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR, search_mask=one_health_vision_mask)


#initialize the action class
rapid_heal_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\rapid_heal.png')
protect_melee_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\protect_melee.png')


sorb_one_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_one.png') #these could all have been the same, or even been an overload. all the potiosn have the same size hitbox
sorb_two_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_two.png')
sorb_three_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_three.png')
sorb_four_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\sorb_four.png')

next_overload_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\nmz melee\\image library\\overload_one.png')#put any overload potion picture here, provided they are all the same size. They must be all the same size for this to work. 



PRAYER_THRESHOLD = .93
POTION_THRESHOLD = .93
FIFTY_ONE_HEALTH_THRESHOLD = .85
ZERO_PRAYER_THRESHOLD = .95
OVERLOAD_OFF_THRESHOLD = .9
MAX_SORB_THRESHOLD = .9
PRAYER_OPEN_THRESHOLD = .8

#set a new one each time
KNOWN_OFFSCREEN_POINT = [1000,500]

def speed():
    speed = np.random.normal(.7,.3)
    while speed > .85 or speed < .6:
        speed = np.random.normal(.75,.08)
    return speed


def tick_dropper(odds=20):
    if np.random.randint(0,odds) == 1:
        
        drop = np.random.uniform(.6,2)
        print('tick dropper! sleeping %s' %drop)
        time.sleep(drop)
    return

def wait():
    wait = (.1 + abs(np.random.normal(0,.05)))
    return wait

while True:
        
    #see if we should prayer pot up
    screenshot = wincap.get_screenshot() 
    zero_prayer_allPoints, zero_prayer_bestPoint, zero_prayer_confidence = zero_prayer_vision.find(screenshot, threshold = POTION_THRESHOLD, debug_mode= 'rectangles', return_mode = 'allPoints + bestPoint + confidence')
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        exit()
    print('debugging! zero prayer confidence %s' %zero_prayer_confidence)

