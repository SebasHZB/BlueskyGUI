from multiprocessing.context import Process
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from bluesky.callbacks.zmq import RemoteDispatcher
from bluesky.callbacks import LivePlot, LiveTable

class ProcessLine(QObject):
    signal = pyqtSignal(object)

class Dispatch_Worker(QThread):
    def __init__(self, *args, axis, address, port, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        self.signals = ProcessLine()
        self.axis = axis
        self.remote_dispatcher = RemoteDispatcher( (address, port) )

    @pyqtSlot()
    def run(self):
        self.remote_dispatcher.start()

    def closed(self):
        return self.remote_dispatcher.closed()

    def add_callback(self, cb):
        self.remote_dispatcher.subscribe(cb)
    
    def clear_callbacks(self):
        self.remote_dispatcher.unsubscribe_all()

    def setup_plan(self, plan):
        self.plan = plan
        self.plan.PRINT_CALLBACK = self.signals.signal.emit
    
    def set_names(self, names, axis):
        self.plan.NAMES = names
        self.plan.PRINTERS = []
        self.plan.PLOTS = []
        self.plots = []
        self.plan.describe_printers()
        self.plan.describe_plots(axis)

        for printer in self.plan.PRINTERS:
            self.add_callback(printer)
        
        for plot in self.plan.PLOTS:
            self.add_callback(plot)

    
    def stop(self):
        self.terminate()