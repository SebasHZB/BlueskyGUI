from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import multiprocessing as mp
import signal
import re
import sys
import time

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
from etc.Ophyd_Simulation import Simulation

        
def execute_RE(plan, sim):
    RE = RunEngine({})
    RE.log.setLevel(logging.INFO)
    
    publisher = Publisher('localhost:5567')
    RE.subscribe(publisher)
    
    sim.start()
    print('Starting Scan...')
    RE(plan)
    print('Scan Done...')
    sim.stop()
    
def proxy():
    print('Starting Proxy...')
    proxy = Proxy(5567, 5568)
    proxy.start()
    
class ProcessLine(QObject):
    signal = pyqtSignal(object)

class RunProcess(QRunnable):
    def __init__(self,*args, axes, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        self.axes = axes
        self.signals = ProcessLine()
        
    @pyqtSlot()
    def run(self):
        self.sim = Simulation()
        
        self.device = InjectionBooster(name='booster', signal=self.sim.signal, motor=self.sim.motor)
        print(self.device.current.name, self.device.offset.name)
        
        self.plan = bp.scan([self.device], self.device.offset, 0, 10, 10)
        
        self.lp = LivePlot(self.device.current.name, x=self.device.offset.name, ax=self.axes, marker='.')
        
        self.lt = LiveTable([self.device.offset, self.device.current])
        
        self.remote()
        self.start_scan()
        
    def remote(self):
        self.remote_dispatcher = RemoteDispatcher( ('localhost', 5568) )
        self.remote_dispatcher.subscribe(self.lp)
        self.remote_dispatcher.subscribe(self.lt)
        self.remote_dispatcher.subscribe(lambda x,y: self.signals.signal.emit('update'))
        t1 = threading.Thread(target=self.remote_dispatcher.start, daemon=True)
        t1.start()
        
    def stop_remote(self):
        self.remote_dispatcher.stop()
        
    
    def start_scan(self):                  
        self.p_proxy = mp.Process(target=proxy)
        self.p_proxy.start()
        
        time.sleep(1)
        
        self.p_scan = mp.Process(target=execute_RE, args=[self.plan, self.sim])
        self.p_scan.start()
        
        self.p_scan.join()
        self.terminate()
        
    def terminate(self):
        self.p_scan.terminate()
        self.p_proxy.terminate()