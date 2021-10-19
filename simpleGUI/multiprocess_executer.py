from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import multiprocessing as mp
import re
import sys
import time
import os

import importlib
import importlib.machinery

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
#from etc.custom_plan2 import Custom_Plan

def execute_RE(plan_file, out_q, in_q):
    plan_file.describe_devices()
    plan_file.describe_plans()
    out_q.put(plan_file.NAMES)
    in_q.get()
    plan_file.run_plans()
    
class ProcessLine(QObject):
    signal = pyqtSignal(object)
    names = pyqtSignal(object)

class RunProcess(QThread):
    def __init__(self,*args, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        self.signals = ProcessLine()
        
    @pyqtSlot()
    def run(self):
        assert(self.plan)

        self.in_q = mp.Queue()
        out_q = mp.Queue()

        self.p_scan = mp.Process(target=execute_RE, args=[self.plan, out_q, self.in_q])
        self.p_scan.start()

        self.signals.names.emit(out_q.get())

        self.p_scan.join()
        self.quit()
    
    def send_to_process(self, msg):
        try:
            self.in_q.put(msg)
        except AttributeError as e:
            print(e)

    def set_plan(self, plan):
        self.plan = plan
        
    def start_remote(self):
        self.remote_dispatcher = RemoteDispatcher( ('localhost', 5568) )

        self.remote_dispatcher.unsubscribe_all()
        
        for printer in self.plan.PRINTERS:
            self.remote_dispatcher.subscribe(printer)
            
        for plot in self.plan.PLOTS:
            self.remote_dispatcher.subscribe(plot)

        t1 = threading.Thread(target=self.remote_dispatcher.start, daemon=True)
        t1.start()
        
    def close_worker(self):
        self.p_scan.terminate()
