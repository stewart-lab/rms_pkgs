#!/usr/bin/env python
import time

# ---------------  FUNCTIONS -------------------
def get_time_and_pretty_time():
    time_struct = time.localtime()
    time_secs = time.mktime(time_struct)  #need to use something besides time.mktime if want fractions of sec.
    #pretty_time = time.strftime("%d_%b_%Y_%H_%M_%S", time_struct)  #old format
    pretty_time = time.strftime("%Y_%m_%d_%H_%M_%S", time_struct)  #New format that will sort better
    return(time_secs, pretty_time)
    
    