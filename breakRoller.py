#breakroller
import numpy as np
import time

def breakRoller(odds=10,minseconds = 60, maxseconds=140):
#this guy determines if it should take a break
    breakroller = np.random.randint(0,odds)
    hibernation_time = (np.random.randint(minseconds,maxseconds)) #breaktime random time between 10-140 seconds
    if breakroller == 1:
        print("Breakroll! hibernating for "+ str(hibernation_time)+ " seconds")
        time.sleep(hibernation_time)
        
    #else:
        #print("breakroller was "+ str(breakroller)+ ". I would have hibernated for "+ str(hibernation_time) + " seconds.")