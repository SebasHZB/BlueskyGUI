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
from bluesky import RunEngine
import bluesky.plans as bp
import logging
from bluesky.callbacks.stream import LiveDispatcher
from bluesky.callbacks import LivePlot, LiveTable

from bluesky.callbacks.zmq import Publisher, Proxy, RemoteDispatcher

from etc.InjectionBooster import InjectionBooster
from etc.Ophyd_Simulation import Simulation
        
def foo(sim, inj):
    #from IPython import embed
    #embed()    
    RE = RunEngine({})
    RE.log.setLevel(logging.INFO)
    
    publisher = Publisher('localhost:5567')
    RE.subscribe(publisher)
    
    sim.start()
    print('hier')
    RE(bp.scan([inj], inj.offset, 0, 10, 10))
    print('done')
    sim.stop()
    
def proxy():
    print('Starting Proxy...')
    proxy = Proxy(5567, 5568)
    proxy.start()
    
def remote(cbs):
    print('Starting RemoteDispatcher...')
    remote = RemoteDispatcher(('localhost', 5568))
    for cb in cbs:
        remote.subscribe(cb)
    remote.start()
    
    
class ProcessLine(QObject):
    signal = pyqtSignal(object)

class RunProcess(QRunnable):
    def __init__(self,*args, axes, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        self.signals = ProcessLine()
        self.axes = axes
        
    @pyqtSlot()
    def run(self):
        self.start()
    
    def start(self):       
        
        sim = Simulation()
        inj = InjectionBooster(name='booster', signal=sim.signal, motor=sim.motor)
        
        lp = LivePlot(inj.current.name, x=inj.offset.name, ax=self.axes, marker='.')
        
    
        lt = LiveTable([inj.offset, inj.current])
        
        p_proxy = mp.Process(target=proxy)
        p_proxy.start()
        
        p_remote = mp.Process(target=remote, args=[ [lt, lp, self.test_cb] ])
        p_remote.start()
        
        p_scan= mp.Process(target=foo, args=[sim, inj])
        p_scan.start()
        
        p_scan.join()
        p_proxy.terminate()
        p_remote.terminate()

    def read(self):
        nextline = self.process.stdout.readline()
        ansi_escape_8bit = re.compile(
            br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
        )
        result = ansi_escape_8bit.sub(b'', nextline)
        return result
        
        
    def write(self, msg):
        self.process.stdin.write(msg)
        
        
    def test_cb(self, *args):
        self.signals.signal.emit(args)
        
    def pause(self):
        if self.paused:
            self.write('RE.resume()')
            self.paused = False
        else:
            self.write("RE.pause()")
            self.paused = True


    def terminate(self):
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)
