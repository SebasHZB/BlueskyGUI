from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import multiprocessing as mp
import re
import sys
import time
import os

import importlib

import threading

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import logging
from bluesky.callbacks import LiveTable
from bluesky.callbacks.mpl_plotting import LivePlot

from bluesky.callbacks.zmq import Publisher, Proxy, RemoteDispatcher

#from etc.custom_plan import Custom_Plan
from etc.simulation_plan import Custom_Plan
        
def execute_RE(thing, out_q, in_q):
    thing.describe_devices()
    thing.describe_plans()
    out_q.put(thing.NAMES)
    in_q.get()
    thing.run_plans()
    
def proxy():
    print('Starting Proxy...')
    proxy = Proxy(5567, 5568)
    proxy.start()
    
class ProcessLine(QObject):
    signal = pyqtSignal(object)

class RunProcess(QRunnable):
    def __init__(self,*args, path, plan_name, axes, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        
        self.axes = axes
        self.signals = ProcessLine()
        
    @pyqtSlot()
    def run(self):        
        #self.lp = LivePlot(self.device.current.name, x=self.device.offset.name, ax=self.axes, marker='.')
        
        self.plan = Custom_Plan()
        self.plan.PRINT_CALLBACK = self.signals.signal.emit
        self.plan.AXIS = self.axes

        in_q = mp.Queue()
        out_q = mp.Queue()

        self.p_scan = mp.Process(target=execute_RE, args=[self.plan, out_q, in_q])
        self.p_scan.start()

        self.plan.NAMES = out_q.get()
        
        self.plan.describe_printers()
        self.plan.describe_plots()
        self.remote()
        self.p_proxy = mp.Process(target=proxy)
        self.p_proxy.start()
        time.sleep(2)
        in_q.put('start scan')

        self.p_scan.join()
        self.terminate()
        
    def remote(self):
        self.remote_dispatcher = RemoteDispatcher( ('localhost', 5568) )
        
        for printer in self.plan.PRINTERS:
            self.remote_dispatcher.subscribe(printer)
            
        for plot in self.plan.PLOTS:
            self.remote_dispatcher.subscribe(plot)
            
        t1 = threading.Thread(target=self.remote_dispatcher.start, daemon=True)
        t1.start()                
        
    def terminate(self):
        self.p_scan.terminate()
        self.p_proxy.terminate()
        
    def close_worker(self):
        self.remote_dispatcher.stop()
        self.terminate()
        print('Dinge')
