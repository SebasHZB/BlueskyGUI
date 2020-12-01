from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ProcessLine(QObject):
    signal = pyqtSignal(object)

class RunProcess(QRunnable):
    def __init__(self,*args,**kwargs):
        QObject.__init__(self,*args, bluesky**kwargs)
        self.signals = ProcessLine()
        self.pause = False

    @pyqtSlot()
    def run(self):
        command = 'python test_plan.py'
        self.process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)

        # Poll process for new output until finished
        while True:
            nextline = self.process.stdout.readline()
            if nextline == '' and self.process.poll() is not None:
                break
            self.signals.signal.emit(nextline)
    
    def start(self):
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )


    def read(self):
        self.signal.emit(self.process.stdout.readline())


    def terminate(self):
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)