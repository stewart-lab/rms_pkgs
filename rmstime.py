#!/usr/bin/env python
import time

# ---------------  FUNCTIONS -------------------
def get_time():
    time_struct = time.localtime()
    time_secs = time.mktime(time_struct)  #need to use something besides time.mktime if want fractions of sec.
    pretty_time = time.strftime("%d_%b_%Y_%H_%M_%S", time_struct)
    return(time_secs, pretty_time)
    
    