#vision.py
import cv2 as cv
import numpy as np

#test = cv.imread('C:\\Users\\Jeff C\\Downloads\\Code\\OpenCV files\\video processing attempt 2\\U.PNG')
#note: if you call find on the same object more than once per loop, it starts to lower the confidence it returns. I have no idea why, it seems crazy, just don't do it. 


class Vision:

    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = cv.TM_CCOEFF_NORMED
    imread = cv.IMREAD_GRAYSCALE
    search_mask = None

    # constructor
    def __init__(self, needle_img_path, method=method, imread=imread, search_mask = search_mask):
        #choose what method to read the image. this must match the imread method for haystack image calls
        #options: cv.IMREAD_COLOR, cv.IMREAD_GRAYSCALE, cv.IMREAD_UNCHANGED
        self.imread = imread        
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.needle_img = cv.imread(needle_img_path, self.imread)

        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

        #the mask is used to find non-square objects. the mask should be the outline of the image in jet black (ie color '0' on the array)
        self.search_mask = search_mask

    def find(self, haystack_img, threshold=0.5, debug_mode=None, return_mode = 'bestPoint'): #note: I added return_mode. it's not tested
        # run the OpenCV algorithm
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method, mask=self.search_mask)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        #print(locations)

        # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
        # locations by using groupRectangles().
        # First we need to create the list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)
        # Apply group rectangles.
        # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
        # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
        # in the result. I've set eps to 0.5, which is:
        # "Relative difference between sides of the rectangles to merge them into a group."
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        #print(rectangles)

        

        #this returns center points of all objects above threshold
        points = []
        if len(rectangles):
            #print('Found needle.')

            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            # Loop over all the rectangles
            for (x, y, w, h) in rectangles:
                '''
                # Determine the center position
                center_x = x + int(w/2)
                center_y = y + int(h/2)
                # Save the points
                points.append((center_x, center_y))
                '''
                #i've commented out the above becuase my click function takes the upper left points of the hitbox as an input, and this would have delivered center points instead. 
                points.append((x,y))

                if debug_mode == 'rectangles':
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                                lineType=line_type, thickness=2)
                elif debug_mode == 'points':
                    # Draw the topleft point
                    cv.drawMarker(haystack_img, (x, y), 
                                color=marker_color, markerType=marker_type, 
                                markerSize=40, thickness=2)

        

        if debug_mode:
            cv.imshow('Matches', haystack_img)
            #cv.waitKey()
            #cv.imwrite('result_click_point.jpg', haystack_img)

        #maxLoc yeilds the best point 
        #ONLY WORKS FOR GRAYSCALE IMAGES CORRECTLLY CONVERTED FROM BGR OR RGB
        minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
        bestPointCenter = [maxLoc[0]+ int(self.needle_w/2), maxLoc[1] + int(self.needle_h/2)] 
        bestPointTopLeft = [maxLoc[0],maxLoc[1]]
        if return_mode == 'bestPoint':
            #print('confidence bestPoint = '+ str(maxVal))
            if maxVal > threshold:
                return bestPointTopLeft
            else:
                return []

        if return_mode == 'allPoints':
            return points

        if return_mode == 'confidence':
            return [bestPointTopLeft,maxVal]

        if return_mode == 'allPoints + bestPoint + confidence':
            return points, bestPointTopLeft,maxVal
        
    def hitboxDims(self): #gives the size of the identified hitbox
        return [self.needle_w, self.needle_h]

