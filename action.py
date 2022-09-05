#actions
from windowcapture import WindowCapture
import numpy as np
import time
from windmouse import wind_mouse
import pyautogui
import cv2 as cv 

#note: try changing the imread color to imread unchanged. I think it may be coding the color channels in a different order than othe rparts of the program expect or something

#note: this expects to receive screencoords of the top left of the needle image. right now I'm using center coords
#it's done and tested mildly. I trust it enough to toss it into main

def tick_dropper(odds=100):
    if np.random.randint(0,odds) == 0:
        print('tick dropper! odds = 1 in %s' %odds)
        time.sleep(.6 + abs(np.random.normal(0,.2)))
    return
    


class Action:
    #parameters
    locus1 = [0,0] #these are the coordinates within the hitbox of the three locuses for clicking. these are defined once per session.  
    locus2 = [0,0]
    locus3 = [0,0]

    hitboxHeight = 0 
    hitboxWidth = 0
    hitboxSmallestDimension = 0 #if hieght<width, this is equal to hieght. If width<height, it's equal to height 

    radius = 0 #this is the radius of the circles in which points are evenly distributed. at the center of each circle is the locus
    stdDev = 0 # standard deviation of the coordinate adjuster 

    #above this line the values are fixed per session, below they are variable
    
    #this is the locus picked to generate a point around
    locusPick = [] 

    #these are the point offsets from the given locus. the hypotenus given by x_offset**2 + y_offset**2 < radius**2
    x_locus_offset = 0
    y_locus_offset = 0

    #this is the point within the locus circle, not yet random walked
    locusPoint = [0,0]

    #the amounts of random walk given to each point after being seated in a circle
    x_pointWalk = 0
    y_pointWalk = 0

    hitboxClickPoint = [] #the location of the generated clickpoint within the hitbox
    screenClickPoint = [] #the location of the generated clickpoint within the screen
    
    hitboxScreenCoords = [] #the location of the upper left corner of the hitbox

    #constructor
    #note: 'click_mask' should be a mask = cv.imread('filelocation',0) type thing, ie a blacka nd white image read by cv.
    #note: face_size should be a list of the approximate face sizes [x size, y size] where face is the area not covered by mask. assume it's roughly rectangular when getting size
    def __init__(self, hitbox_img_path, click_mask = [], face_size = None):
        self.hitboxImage = cv.imread(hitbox_img_path,cv.IMREAD_COLOR)
        self.mask = click_mask
        self.face_size = face_size


        #calculate the hitbox height and width using info from hitbox image
        self.hitboxWidth = self.hitboxImage.shape[1]
        self.hitboxHeight = self.hitboxImage.shape[0]
    

        #the constructor will set up the locuses, radius, and stdDev which will remain constant for the duration of the session
        

        #determine the smallest hitbox dimension
        if self.mask == []: #this means we're not doing mask, and the standard dev should be a function of the total image size
            if self.hitboxWidth < self.hitboxHeight:
                self.hitboxSmallestDimension = self.hitboxWidth
            else:
                self.hitboxSmallestDimension = self.hitboxHeight

        else: #if we're doing mask, stddev should be made with reference to face_size instead of total image size
            if self.face_size[0] < self.face_size[1]:
                self.hitboxSmallestDimension = self.face_size[0]
            if self.face_size[0] > self.face_size[1]:
                self.hitboxSmallestDimension = self.face_size[1]
            else:
                self.hitboxSmallestDimension = self.face_size[0]

        #determine the radius of the locus circles
        self.radius = (2/15)* self.hitboxSmallestDimension

        #determine the stdDev
        self.stdDev = (1/15)* self.hitboxSmallestDimension

        #the stdDev and radius values are calculated to create some overlap of the circles, but not too much, and to keep 999/1000 clicks within the hitbox

        # if we're doing no mask, this will roll locus points somewhere within 5.5 stdDev of the image border.
        if self.mask == []:
            #pick locus points for the session
            locus1_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
            locus1_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
            self.locus1 = [locus1_x,locus1_y]
            
            #this will make locus 2 
            locus2_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
            locus2_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
            self.locus2 = [locus2_x,locus2_y]
            
            '''
            #this will reroll locus2 until it is at least one radius away from locus1. the complicated expression is just the pythagorean theorem
            while (((np.absolute(self.locus1[0]) - np.absolute(self.locus2[0])) **2) + ((np.absolute(self.locus1[1]) -np.absolute(self.locus2[1])) **2)) < (self.radius **2):
                print('Too close! locus1 = ' + str(self.locus1)+' locus2 = ' + str(self.locus2))
                locus2_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
                locus2_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
                self.locus2 = [locus2_x,locus2_y]
            '''

            #this will make locus 3 
            locus3_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
            locus3_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
            self.locus3 = [locus3_x,locus3_y]

            '''
            #this will reroll locus3 until it is at least one radius away from both locus1 and locus2
            while(  (((np.absolute(self.locus1[0]) - np.absolute(self.locus3[0])) **2) + ((np.absolute(self.locus1[1]) - np.absolute(self.locus3[1])) **2)) < (self.radius **2) or 
            (((np.absolute(self.locus2[0]) - np.absolute(self.locus3[0])) **2) + ((np.absolute(self.locus2[1]) - np.absolute(self.locus3[1])) **2)) < (self.radius **2)):
                print('Too close! locus1 = ' + str(self.locus1)+' locus2 = ' + str(self.locus2)+ ' locus3 = ' + str(self.locus3))
                locus3_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
                locus3_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
                self.locus3 = [locus3_x,locus3_y]
            '''
        #if we're doing mask, this will roll locus points at least 5.5 stddev away from the image border AND within the face region
        if self.mask != []:
            #pick locus points for the session
            locus1_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
            locus1_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
            self.locus1 = [locus1_x,locus1_y]
            locus1_mask_check = self.mask[locus1_y,locus1_x]
            
            #this checks to see if we've rolled onto the mask. If so we reroll until we're on the face.
            while locus1_mask_check == 0:
                print('locus 1 = %s | mask_check = %s | rerolling' %(self.locus1, locus1_mask_check))
                locus1_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
                locus1_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
                self.locus1 = [locus1_x,locus1_y]
                locus1_mask_check = self.mask[locus1_y,locus1_x]

            print('locus 1 = %s | mask_check = %s | locked in' %(self.locus1, locus1_mask_check))

            #this will make locus 2 
            locus2_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
            locus2_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
            self.locus2 = [locus2_x,locus2_y]
            locus2_mask_check = self.mask[locus2_y,locus2_x]

            while locus2_mask_check == 0:
                print('locus 2 = %s | mask_check = %s | rerolling' %(self.locus2, locus2_mask_check))
                locus2_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
                locus2_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
                self.locus2 = [locus2_x,locus2_y]
                locus2_mask_check = self.mask[locus2_y,locus2_x]

            print('locus 2 = %s | mask_check = %s | locked in' %(self.locus2, locus2_mask_check))

            #this will make locus 3 
            locus3_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
            locus3_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
            self.locus3 = [locus3_x,locus3_y]
            locus3_mask_check = self.mask[locus3_y,locus3_x]
            
            #this checks to see if we've rolled onto the mask. If so we reroll until we're on the face.
            while locus3_mask_check == 0:
                print('locus 1 = %s | mask_check = %s | rerolling' %(self.locus3, locus3_mask_check))
                locus3_x = np.random.randint(round((5.5*self.stdDev)),((self.hitboxWidth - round(5.5*self.stdDev))+1)) #this creates a random x coord that is at least 5.5 stdDev away from the hitbox boundary
                locus3_y = np.random.randint(round((5.5*self.stdDev)),((self.hitboxHeight - round(5.5*self.stdDev))+1))
                self.locus3 = [locus3_x,locus3_y]
                locus3_mask_check = self.mask[locus3_y,locus3_x]

            print('locus 3 = %s | mask_check = %s | locked in' %(self.locus3, locus3_mask_check))


     
    def click(self,hitboxScreenCoords,speed=.65, wait= (.12 + abs(np.random.uniform(0,.02))), no_post_click_wait = False, tick_dropper_odds = 100):
        self.hitboxScreenCoords = hitboxScreenCoords
    

        #pick a locus to generate a point int
        locusPicker = np.random.randint(1,4)
        if locusPicker == 1:
            self.locusPick = self.locus1
        if locusPicker == 2:
            self.locusPick = self.locus2
        if locusPicker == 3:
            self.locusPick = self.locus3
    
        #generate the locus offset
        self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
        #account for the possible case of a negative y_locus_offset
        if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
            self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
        else:
            self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
        #calculate the point within the locus. these are hitbox coords
        self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

        #randomly walk the point within the locus
        self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
        self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

        #put this into the hitboxClickPoint
        self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

        #check we haven't wandered out of bounds, if so reroll until we're in bounds
        while self.hitboxClickPoint[0] < 0 or self.hitboxClickPoint[0] > self.hitboxWidth or self.hitboxClickPoint[1] < 0 or self.hitboxClickPoint[1] > self.hitboxHeight:
            #pick a locus to generate a point int
            locusPicker = np.random.randint(1,4)
            if locusPicker == 1:
                self.locusPick = self.locus1
            if locusPicker == 2:
                self.locusPick = self.locus2
            if locusPicker == 3:
                self.locusPick = self.locus3
        
            #generate the locus offset
            self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
            #account for the possible case of a negative y_locus_offset
            if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
            else:
                self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
            #calculate the point within the locus. these are hitbox coords
            self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

            #randomly walk the point within the locus
            self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
            self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

            #put this into the hitboxClickPoint
            self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

        #check if we're doing a mask
        if self.mask != []:
            
            #ok, we're doing a mask. We check to see if the clickpoint coords at the mask image are black. if so, we're going to reroll clickpoint.
            #note: mask is a np array, and coords are expressed in [y,x] instead of [x,y]
            #convert hitbox clickpoint from [x,y] to [y],[x]. also turn it into an integer.
            self.hitboxClickPoint_x = round(self.hitboxClickPoint[0])
            self.hitboxClickPoint_y = round(self.hitboxClickPoint[1])
            
            #check the color of the mask at hitboxClickPoint
            self.hitboxClickPoint_mask_check = self.mask[self.hitboxClickPoint_y, self.hitboxClickPoint_x]
            print('hitbox clickpoint = %s | mask_check = %s' % (self.hitboxClickPoint, self.hitboxClickPoint_mask_check))
            
            #while the color of the mask at point is black (==0), reroll
            while self.hitboxClickPoint_mask_check == 0:
                #pick a locus to generate a point int
                locusPicker = np.random.randint(1,4)
                if locusPicker == 1:
                    self.locusPick = self.locus1
                if locusPicker == 2:
                    self.locusPick = self.locus2
                if locusPicker == 3:
                    self.locusPick = self.locus3
    
                #generate the locus offset
                self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
                #account for the possible case of a negative y_locus_offset
                if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                    self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
                else:
                    self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
                #calculate the point within the locus. these are hitbox coords
                self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

                #randomly walk the point within the locus
                self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
                self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

                #put this into the hitboxClickPoint
                self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

                #check we haven't wandered out of bounds, if so reroll until we're in bounds
                while self.hitboxClickPoint[0] < 0 or self.hitboxClickPoint[0] > self.hitboxWidth or self.hitboxClickPoint[1] < 0 or self.hitboxClickPoint[1] > self.hitboxHeight:
                    #pick a locus to generate a point int
                    locusPicker = np.random.randint(1,4)
                    if locusPicker == 1:
                        self.locusPick = self.locus1
                    if locusPicker == 2:
                        self.locusPick = self.locus2
                    if locusPicker == 3:
                        self.locusPick = self.locus3
                
                    #generate the locus offset
                    self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
                    #account for the possible case of a negative y_locus_offset
                    if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                        self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
                    else:
                        self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
                    #calculate the point within the locus. these are hitbox coords
                    self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

                    #randomly walk the point within the locus
                    self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
                    self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

                    #put this into the hitboxClickPoint
                    self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

                #note: mask is a np array, and coords are expressed in [y,x] instead of [x,y]
                #convert hitbox clickpoint from [x,y] to [y],[x]. also turn it into an integer.
                self.hitboxClickPoint_x = int(self.hitboxClickPoint[0])
                self.hitboxClickPoint_y = int(self.hitboxClickPoint[1])
                
                #check the color of the mask at hitboxClickPoint
                self.hitboxClickPoint_mask_check = self.mask[self.hitboxClickPoint_y, self.hitboxClickPoint_x]
                print('hitbox clickpoint = %s | mask_check = %s' % (self.hitboxClickPoint, self.hitboxClickPoint_mask_check ))


        #put this into the screenClickPoint
        self.screenClickPoint = [self.hitboxClickPoint[0] + self.hitboxScreenCoords[0], self.hitboxClickPoint[1] + self.hitboxScreenCoords[1]]

        #move mouse to clickpoint
        wind_mouse(pyautogui.position()[0], pyautogui.position()[1], self.screenClickPoint[0], self.screenClickPoint[1], speed=speed)
        tick_dropper(odds = tick_dropper_odds)
        time.sleep(wait)
        pyautogui.click()
        if no_post_click_wait == False:
            time.sleep(wait)
        else:
            print('clicked with no post_click_wait')
        #if np.random.random() < .3: #triggered 30% of the time #update: I think this is worse than nothing so I'm commenting it out
        #    pyautogui.moveRel(np.random.randint(-5,6),np.random.randint(-5,6)) #I'm throwing this in here so that the mouse moves a little bit after clicking
        
        return self.screenClickPoint

    def moveTo(self,hitboxScreenCoords,speed=.65, wait= (.12 + abs(np.random.uniform(0,.02)))):
        self.hitboxScreenCoords = hitboxScreenCoords
    
        #pick a locus to generate a point int
        locusPicker = np.random.randint(1,4)
        if locusPicker == 1:
            self.locusPick = self.locus1
        if locusPicker == 2:
            self.locusPick = self.locus2
        if locusPicker == 3:
            self.locusPick = self.locus3
    
        #generate the locus offset
        self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
        #account for the possible case of a negative y_locus_offset
        if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
            self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
        else:
            self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
        #calculate the point within the locus. these are hitbox coords
        self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

        #randomly walk the point within the locus
        self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
        self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

        #put this into the hitboxClickPoint
        self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

        #check we haven't wandered out of bounds, if so reroll until we're in bounds
        while self.hitboxClickPoint[0] < 0 or self.hitboxClickPoint[0] > self.hitboxWidth or self.hitboxClickPoint[1] < 0 or self.hitboxClickPoint[1] > self.hitboxHeight:
            #pick a locus to generate a point int
            locusPicker = np.random.randint(1,4)
            if locusPicker == 1:
                self.locusPick = self.locus1
            if locusPicker == 2:
                self.locusPick = self.locus2
            if locusPicker == 3:
                self.locusPick = self.locus3
        
            #generate the locus offset
            self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
            #account for the possible case of a negative y_locus_offset
            if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
            else:
                self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
            #calculate the point within the locus. these are hitbox coords
            self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

            #randomly walk the point within the locus
            self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
            self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

            #put this into the hitboxClickPoint
            self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

        #check if we're doing a mask
        if self.mask != []:
            
            #ok, we're doing a mask. We check to see if the clickpoint coords at the mask image are black. if so, we're going to reroll clickpoint.
            #note: mask is a np array, and coords are expressed in [y,x] instead of [x,y]
            #convert hitbox clickpoint from [x,y] to [y],[x]. also turn it into an integer.
            self.hitboxClickPoint_x = round(self.hitboxClickPoint[0])
            self.hitboxClickPoint_y = round(self.hitboxClickPoint[1])
            
            #check the color of the mask at hitboxClickPoint
            self.hitboxClickPoint_mask_check = self.mask[self.hitboxClickPoint_y, self.hitboxClickPoint_x]
            print('hitbox clickpoint = %s | mask_check = %s' % (self.hitboxClickPoint, self.hitboxClickPoint_mask_check))
            
            #while the color of the mask at point is black (==0), reroll
            while self.hitboxClickPoint_mask_check == 0:
                #pick a locus to generate a point int
                locusPicker = np.random.randint(1,4)
                if locusPicker == 1:
                    self.locusPick = self.locus1
                if locusPicker == 2:
                    self.locusPick = self.locus2
                if locusPicker == 3:
                    self.locusPick = self.locus3
    
                #generate the locus offset
                self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
                #account for the possible case of a negative y_locus_offset
                if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                    self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
                else:
                    self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
                #calculate the point within the locus. these are hitbox coords
                self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

                #randomly walk the point within the locus
                self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
                self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

                #put this into the hitboxClickPoint
                self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

                #check we haven't wandered out of bounds, if so reroll until we're in bounds
                while self.hitboxClickPoint[0] < 0 or self.hitboxClickPoint[0] > self.hitboxWidth or self.hitboxClickPoint[1] < 0 or self.hitboxClickPoint[1] > self.hitboxHeight:
                    #pick a locus to generate a point int
                    locusPicker = np.random.randint(1,4)
                    if locusPicker == 1:
                        self.locusPick = self.locus1
                    if locusPicker == 2:
                        self.locusPick = self.locus2
                    if locusPicker == 3:
                        self.locusPick = self.locus3
                
                    #generate the locus offset
                    self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
                    #account for the possible case of a negative y_locus_offset
                    if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                        self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
                    else:
                        self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
                    #calculate the point within the locus. these are hitbox coords
                    self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

                    #randomly walk the point within the locus
                    self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
                    self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

                    #put this into the hitboxClickPoint
                    self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

                #note: mask is a np array, and coords are expressed in [y,x] instead of [x,y]
                #convert hitbox clickpoint from [x,y] to [y],[x]. also turn it into an integer.
                self.hitboxClickPoint_x = round(self.hitboxClickPoint[0])
                self.hitboxClickPoint_y = round(self.hitboxClickPoint[1])
                
                #check the color of the mask at hitboxClickPoint
                self.hitboxClickPoint_mask_check = self.mask[self.hitboxClickPoint_y, self.hitboxClickPoint_x]
                print('hitbox clickpoint = %s | mask_check = %s' % (self.hitboxClickPoint, self.hitboxClickPoint_mask_check ))


        #put this into the screenClickPoint
        self.screenClickPoint = [self.hitboxClickPoint[0] + self.hitboxScreenCoords[0], self.hitboxClickPoint[1] + self.hitboxScreenCoords[1]]

        #move mouse to clickpoint
        wind_mouse(pyautogui.position()[0], pyautogui.position()[1], self.screenClickPoint[0], self.screenClickPoint[1], speed=speed)
        time.sleep(wait)
        #pyautogui.click()
        #time.sleep(wait)
        #if np.random.random() < .3: #triggered 30% of the time #update: I think this is worse than nothing so I'm commenting it out
        #    pyautogui.moveRel(np.random.randint(-5,6),np.random.randint(-5,6)) #I'm throwing this in here so that the mouse moves a little bit after clicking
        
        return self.screenClickPoint

    def dropClick(self, hitboxScreenCoords,speed =.5):
            self.hitboxScreenCoords = hitboxScreenCoords
            
            #pick a locus to generate a point int
            locusPicker = np.random.randint(1,4)
            if locusPicker == 1:
                self.locusPick = self.locus1
            if locusPicker == 2:
                self.locusPick = self.locus2
            if locusPicker == 3:
                self.locusPick = self.locus3
        
            #generate the locus offset
            self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
            #account for the possible case of a negative y_locus_offset
            if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
                self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
            else:
                self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
            #calculate the point within the locus. these are hitbox coords
            self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

            #randomly walk the point within the locus
            self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
            self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

            #put this into the hitboxClickPoint
            self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

            #put this into the screenClickPoint
            self.screenClickPoint = [self.hitboxClickPoint[0] + self.hitboxScreenCoords[0], self.hitboxClickPoint[1] + self.hitboxScreenCoords[1]]

            #move mouse to clickpoint
            wind_mouse(pyautogui.position()[0], pyautogui.position()[1], self.screenClickPoint[0], self.screenClickPoint[1],speed=speed)
            pyautogui.keyDown('shift')
            time.sleep(abs(np.random.normal(.09,.03)))
            pyautogui.click()
            #if np.random.randint(1,7) == 7: 
            #    pyautogui.moveRel(np.random.randint(-5,6)) #I'm throwing this in here so that the mouse moves a little bit after clicking
            #time.sleep(np.random.normal(.1,.02))
            return self.screenClickPoint

    def rightClick(self,hitboxScreenCoords,speed=.5, wait= (.06 + abs(np.random.uniform(0,.02)))):
        self.hitboxScreenCoords = hitboxScreenCoords

        #pick a locus to generate a point int
        locusPicker = np.random.randint(1,4)
        if locusPicker == 1:
            self.locusPick = self.locus1
        if locusPicker == 2:
            self.locusPick = self.locus2
        if locusPicker == 3:
            self.locusPick = self.locus3
    
        #generate the locus offset
        self.x_locus_offset = np.random.randint(round(self.radius*-2), (round(self.radius*2)+1))
        #account for the possible case of a negative y_locus_offset
        if ((self.radius ** 2) - (self.x_locus_offset ** 2)) < 0:
            self.y_locus_offset = np.sqrt(np.absolute((self.radius ** 2) - (self.x_locus_offset ** 2)))*-1
        else:
            self.y_locus_offset = np.sqrt((self.radius ** 2) - (self.x_locus_offset ** 2))
        #calculate the point within the locus. these are hitbox coords
        self.locusPoint = [self.locusPick[0] + self.x_locus_offset, self.locusPick[1] + self.y_locus_offset]

        #randomly walk the point within the locus
        self.x_pointWalk = np.random.normal(loc=0, scale=self.stdDev)
        self.y_pointWalk = np.random.normal(loc=0, scale=self.stdDev)

        #put this into the hitboxClickPoint
        self.hitboxClickPoint = [self.locusPoint[0]+ self.x_pointWalk, self.locusPoint[1]+self.y_pointWalk]

        #put this into the screenClickPoint
        self.screenClickPoint = [self.hitboxClickPoint[0] + self.hitboxScreenCoords[0], self.hitboxClickPoint[1] + self.hitboxScreenCoords[1]]

        #move mouse to clickpoint
        wind_mouse(pyautogui.position()[0], pyautogui.position()[1], self.screenClickPoint[0], self.screenClickPoint[1], speed=speed)
        time.sleep(wait)
        pyautogui.rightClick()
        time.sleep(wait)
        #if np.random.random() < .3: #triggered 30% of the time #update: I think this is worse than nothing so I'm commenting it out
        #    pyautogui.moveRel(np.random.randint(-5,6),np.random.randint(-5,6)) #I'm throwing this in here so that the mouse moves a little bit after clicking
        
        return self.screenClickPoint

    #experimental below!
    #maskClick takes a 'mask' image of the same size as the main image. If a click is generated that falls on the mask, it doesn't execute the click and rerolls until it hits on the unmasked area.

    