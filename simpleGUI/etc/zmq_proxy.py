from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from bluesky.callbacks.zmq import Proxy

class Proxy_Worker(QThread):
    def __init__(self, *args, portIN, portOUT, **kwargs):
        QObject.__init__(self,*args, **kwargs)
        self.zmq_proxy = Proxy(in_port=portIN, out_port=portOUT)

    @pyqtSlot()
    def run(self):
        self.zmq_proxy.start()
    
    def closed(self):
        return self.zmq_proxy.closed

    def stop(self):
        self.terminate()