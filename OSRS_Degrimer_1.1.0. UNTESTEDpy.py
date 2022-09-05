# degrimer, taken from superglass make. I'm going to add an esc key close, and session specific wait parameters. 
#innovations: I'm putting some in, like how there are session specific efficiency parameters, and how it gets more tired as a preportion of remaining run time. 

#todo
#finish the new timing system (session specific time variables)
#finish the xp drop vision and xp drop vision check
#change the filepaths of the reference images. 

from re import search
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
import breakRoller

# initialize the WindowCapture class
wincap = WindowCapture('RuneLite - Vessacks')


# initialize the Vision class
weed_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\weed.png', method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
bank_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\bank.png',method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
bank_dump_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\bank_dump.png',method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)
spellcast_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\spellcast.png',method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_GRAYSCALE)

#this guy is masked and in color
xp_drop_search_mask = cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\xp_drop_search_mask.png', cv.IMREAD_COLOR)
xp_drop_vision = Vision('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\xp_drop.png',method = cv.TM_CCOEFF_NORMED, imread = cv.IMREAD_COLOR, search_mask=xp_drop_search_mask)

#initialize the action class
weed_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\weed.png')
bank_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\bank.png')
bank_dump_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\bank_dump.png')
spellcast_action = Action('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\superglass make\\image library\\spellcast.png')

#todo:
#1 when you're done, remove the debug mode and stop drawing the screen for speed
#2 test your theory about putting waitkeys and new screenshots in between all actions

#notes: start next to bank, inventory contents don't matter
#I've set up imshows and new screenshots for every action because I think that reduces opencv fuckups. remember-- if you perform the same operation twice in a row without this you CAN get reduced confidence like crazy

#setup
#1 set up a new bank image
#2 have bank withdraw set to all
#3 have bank set to tab with grimy weed, no clean weeds in site and no weeds in the thumbnail
#4 have earth staff equipped
#5 have arceuus spellbook  OPEN
#6 have nature runes in inventory, all bank fillers full, and no filler for nature runes (ie it can't dump nature runes in bank)
#7 this last point is important or it will dump nats in the bank and not have any runes to cast the spell

BANK_THRESHOLD = .63
BANK_THRESHOLD_RECLICK = .2
BANK_DUMP_THRESHOLD = .85
SPELLCAST_THRESHOLD = .85
WEED_THRESHOLD = .85
MAX_FATIGUE = .1 #this is the maximum number of seconds added to each wait action. fatigue editions will occur as a proportion of this value  
XP_DROP_THRESHOLD = .99

wait_time_mean = np.random.uniform()

#WITHDRAW_18_OFFSET = [-117,64] #these are the coord offsets between a righclick point and the withdraw 18 dropdown option


s_or_c = input('would you like to run in seconds or counts? please enter \'s\' or \'c\'')

if s_or_c == 's':
    quit_after_seconds = float(input('please enter the number of seconds to run for, then press enter. 1h = 3600s, 6h = 21600'))
elif s_or_c == 'c':
    quit_after_counts = int(input('please enter the number of counts to run for, then press enter. about 8s per count.'))
else:
    print('you\'ve screwed something up. try running this program again. exiting...')
    exit()

runStart = time.time()
count = 0

def wait():
    wait = (.06 + abs(np.random.uniform(0,.02)))
    return wait

def speed():
    speed = np.random.normal(.78,.3)
    while speed > .85 or speed < .6:
        speed = np.random.normal(.75,.08)
    return speed

def tick_dropper(odds=100):
    if np.random.randint(0,odds) == 1:
        time.sleep(.6)



def superglass_make():    
    while True:

        #waiting a bit for spell to cast
        sleepytime = 1.8 + abs(np.random.normal(0,.1))
        time.sleep(sleepytime)        

                
        #enter bank
        screenshot = wincap.get_screenshot()
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
        bank_confidence = bank_vision.find(screenshot, threshold = BANK_THRESHOLD, return_mode= 'confidence')
        if bank_confidence[1] < BANK_THRESHOLD:
            print(' PROBLEM(!) bank confidence %s | BANK_THRESHOLD %s | Continuing anyway...' %( bank_confidence[1], BANK_THRESHOLD))
            #exit()
        else:
            print('bank confidence %s | BANK_THRESHOLD %s | Continuing...' %( bank_confidence[1], BANK_THRESHOLD))
        bank_screenPoint = wincap.get_screen_position(bank_confidence[0])
        bank_clickPoint = bank_action.click(bank_screenPoint, speed = speed(), wait = wait())
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
        
        #look for bank dump: this takes a variable amount of time
        bank_dump_confidence = [[0,0],0]
        search_start = time.time()
        search_time = 0
        while bank_dump_confidence[1] < BANK_DUMP_THRESHOLD:
            screenshot = wincap.get_screenshot()
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
            bank_dump_confidence = bank_dump_vision.find(screenshot, threshold = BANK_DUMP_THRESHOLD, return_mode= 'confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()

            search_time = time.time() - search_start
            if search_time > 2:
                screenshot = wincap.get_screenshot()
                screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
                bank_confidence = bank_vision.find(screenshot, threshold = BANK_THRESHOLD, return_mode= 'confidence')
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    exit()
                if bank_confidence[1] < BANK_THRESHOLD_RECLICK:
                    print('2+ seconds since bank click. PROBLEM(!) bank confidence %s below BANK_THRESHOLD DISABLED(!) %s | continuing anyway...' %( bank_confidence[1], BANK_THRESHOLD))
                    exit()
                else:
                    print('2+ seoncds inactivity. attempting reclick on bank and sleeping ~.6s. bank confidence %s | BANK_THRESHOLD DISABLED(!) %s | Continuing...' %( bank_confidence[1], BANK_THRESHOLD))
                bank_screenPoint = wincap.get_screen_position(bank_confidence[0])
                bank_clickPoint = bank_action.click(bank_screenPoint, speed = speed(),wait = wait())
                #wait to get to bank
                time.sleep(.3 + abs(np.random.normal(0,.3)))
                #check if recovery worked
                screenshot = wincap.get_screenshot()
                screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
                bank_dump_confidence = bank_dump_vision.find(screenshot, threshold = BANK_DUMP_THRESHOLD, return_mode= 'confidence')
                if cv.waitKey(1) == ord('q'):
                    cv.destroyAllWindows()
                    exit()
                if bank_dump_confidence[1] > BANK_DUMP_THRESHOLD:
                    print('in_bank confidence = %s. reclick worked, continuing...' % bank_dump_confidence[1])
                    break


            if search_time > 20:
                print('PROBLEM(!) 20s+ inactivity. multiple reclicks failed. giving up, exitting...')
                exit()
        

        #this code should be redundant but I'm leaving it in anyway for debugging
        
        if bank_dump_confidence[1] < BANK_DUMP_THRESHOLD:
            print('bank_dump_confidence %s | BANK_DUMP_THRESHOLD %s | Exiting...' %( bank_dump_confidence[1], BANK_DUMP_THRESHOLD))
            exit()
        else:
            print('bank_dump_confidence %s | BANK_DUMP_THRESHOLD %s | Continuing...' %( bank_dump_confidence[1], BANK_DUMP_THRESHOLD))
        
        #click the bank dump
        bank_dump_screenPoint = wincap.get_screen_position(bank_dump_confidence[0])
        bank_dump_clickPoint = bank_dump_action.click(bank_dump_screenPoint, speed = speed(),wait = wait())

        tick_dropper()


        #take all weed (herbs)
        screenshot = wincap.get_screenshot()
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
        weed_confidence = weed_vision.find(screenshot, threshold = WEED_THRESHOLD, debug_mode= 'rectangles', return_mode= 'confidence')
        if weed_confidence[1] < WEED_THRESHOLD:
            print('weed confidence %s | WEED_THRESHOLD %s | Exiting...' %( weed_confidence[1], WEED_THRESHOLD))
            exit()
        else:
            print('weed confidence %s | WEED_THRESHOLD %s | Continuing...' %( weed_confidence[1], WEED_THRESHOLD))
        weed_screenPoint = wincap.get_screen_position(weed_confidence[0])
        weed_clickPoint = weed_action.click(weed_screenPoint, speed = speed(), wait = wait())
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()    

        tick_dropper()

        #exit the bank
        pyautogui.keyDown('esc')
        time.sleep(.08 + np.random.normal(0,.08))
        pyautogui.keyUp('esc')

        #wait a bit before casting spell
        #integrate this into the new system of variable and icnreasingly sleepy wait times
        sleepytime = .15 + abs(np.random.normal(0,.05))
        time.sleep(sleepytime)

        #check here for an xp drop to make sure there isn't an XP drop false positive
        #NOTE: IN COLOR
        screenshot = wincap.get_screenshot()
        xp_drop_confidence = xp_drop_vision.find(screenshot, threshold = XP_DROP_THRESHOLD, debug_mode= 'rectangles', return_mode= 'confidence')
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()
        if xp_drop_confidence > XP_DROP_THRESHOLD:
            print('TROUBLE! I see XP drop BEFORE casting spell | confidence %s | I have no plan for this... exiting. ' % xp_drop_confidence)
            exit()



        #cast spell
        screenshot = wincap.get_screenshot()
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
        spellcast_confidence = spellcast_vision.find(screenshot, threshold = SPELLCAST_THRESHOLD, debug_mode= 'rectangles', return_mode= 'confidence')
        if spellcast_confidence[1] < SPELLCAST_THRESHOLD:
            print('spellcast confidence %s | SPELLCAST_THRESHOLD %s | exitting...' %( spellcast_confidence[1], SPELLCAST_THRESHOLD))
            exit()
        else:
            print('spellcast confidence %s | SPELLCAST_THRESHOLD %s | Continuing...' %( spellcast_confidence[1], SPELLCAST_THRESHOLD))
        spellcast_screenPoint = wincap.get_screen_position(spellcast_confidence[0])
        spellcast_clickPoint = spellcast_action.click(spellcast_screenPoint, speed = speed(), wait = wait())
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            exit()        


        #wait until it sees xp drop
        #NOTE: IN COLOR
        search_start = time.time()
        while True:
            screenshot = wincap.get_screenshot()
            xp_drop_confidence = xp_drop_vision.find(screenshot, threshold = XP_DROP_THRESHOLD, debug_mode= 'rectangles', return_mode= 'confidence')
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                exit()
            if xp_drop_confidence > XP_DROP_THRESHOLD:
                print(' I see XP drop | confidence %s | spellcast success...' % xp_drop_confidence)
                break
            
            if time.time() - search_start > 10:
                print('waited %s and found no XP drop above threshold | best confidence unclear | exitting...')
                exit()


        #debuggery below
        if s_or_c == 's':
            runTime = time.time() - runStart
            if runTime >= quit_after_seconds:
                print('finished after running for %s seconds' % runTime)
                exit()
            print('runtime = %s | seconds remaining = %s' %(runTime, (quit_after_seconds - runTime)))
        if s_or_c == 'c':
            global count
            count = count + 1
            if count >= quit_after_counts:
                print('finished after running %s counts. exitting.. ' % count)
                exit()
            print('count = %s | counts remaining %s' % (count, (quit_after_counts - count)))

while True:
    superglass_make()
    breakRoller.breakRoller(odds = 300, minseconds = 60, maxseconds = 200)
