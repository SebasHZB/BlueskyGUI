from bluesky import RunEngine
from bluesky.callbacks import LivePlot
from bluesky.callbacks.zmq import Publisher
import logging
import time

class Base_Plan():
    
    DEVICES = {}
    PLOTS = []
    PLANS = []
    PRINTERS = []
    PRINT_CALLBACK = print
    AXIS = None
    NAMES = {}
    CUR_AX = None
    
    def __init__(self):
        pass
    
    def describe_device(self):
        raise NotImplementedError
        
    def describe_plot(self):
        raise NotImplementedError
        
    def describe_plan(self):
        raise NotImplementedError
        
    def describe_printers(self):
        raise NotImplementedError
        
    def run_plans(self):
        RE = RunEngine({})
        RE.log.setLevel(logging.INFO)
    
        publisher = Publisher('localhost:5567')
        RE.subscribe(publisher)
        
        for plan in self.PLANS:
            print('Starting Scan...')
            RE(plan)
            print('Scan Done...')
            time.sleep(1)
            
        
    
