from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import multiprocessing as mp
import signal
import re
import sys
import time
import os

import importlib

import threading

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import bluesky
from bluesky import RunEngine, Msg
import bluesky.plans as bp
import logging
from bluesky.callbacks.stream import LiveDispatcher
from bluesky.callbacks import LiveTable
from bluesky.callbacks.mpl_plotting import LivePlot

from bluesky.callbacks.zmq import Publisher, Proxy, RemoteDispatcher

from etc.InjectionBooster import InjectionBooster
from etc.custom_plan import Custom_Plan

from ophyd.sim import FakeEpicsSignal
        
def execute_RE(plans):
    RE = RunEngine({})
    RE.log.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler('bluesky.log')
    logger = logging.getLogger('bluesky')
    logger.addHandler(file_handler)
    file_handler.setLevel(logging.DEBUG)
    
    publisher = Publisher('localhost:5567')
    RE.subscribe(publisher)
    
    print('Starting Scan...')
    RE(plans)
    print('Scan Done...')
    
def proxy():
    print('Starting Proxy...')
    proxy = Proxy(5567, 5568)
    proxy.start()
    
class ProcessLine(QObject):
    signal = pyqtSignal(object)

class RunProcess(QRunnable):
    def __init__(self,*args, path, plan_name, axes, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        
        spec = importlib.util.spec_from_file_location(plan_name, path)
        self.plan = spec.loader.load_module()
        
        self.axes = axes
        self.signals = ProcessLine()
        
    @pyqtSlot()
    def run(self):
        #self.plan = bp.scan([self.device], self.device.offset, 0, 10, 10)
        
        #self.lp = LivePlot(self.device.current.name, x=self.device.offset.name, ax=self.axes, marker='.')
        
        self.thing = Custom_Plan()
        self.thing.PRINT_CALLBACK = self.signals.signal.emit
        self.thing.describe_devices()
        self.thing.describe_printers()
        self.thing.describe_plans()
        self.thing.describe_plots(self.axes)
        
        #self.lt = LiveTable([self.device.offset, self.device.current], out=self.signals.signal.emit)
        
        self.remote()
        self.start_scan()
        
    def remote(self):
        self.remote_dispatcher = RemoteDispatcher( ('localhost', 5568) )
        #self.remote_dispatcher.subscribe(self.lp)
        #self.remote_dispatcher.subscribe(self.lt)
        #self.remote_dispatcher.subscribe(lambda x,y: self.signals.signal.emit('update'))
        for printer in self.thing.PRINTERS:
            self.remote_dispatcher.subscribe(printer)
            
        for plot in self.thing.PLOTS:
            self.remote_dispatcher.subscribe(plot)
            
        t1 = threading.Thread(target=self.remote_dispatcher.start, daemon=True)
        t1.start()        
    
    def start_scan(self):                  
        self.p_proxy = mp.Process(target=proxy)
        self.p_proxy.start()
        
        time.sleep(2)
        
        self.p_scan = mp.Process(target=execute_RE, args=[self.thing.PLANS[0]])
        self.p_scan.start()
        
        self.p_scan.join()
        self.terminate()
        
    def terminate(self):
        self.p_scan.terminate()
        self.p_proxy.terminate()
        
    def close_worker(self):
        self.remote_dispatcher.stop()
        self.terminate()