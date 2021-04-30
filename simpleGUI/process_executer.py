from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import subprocess
import signal
import re

class ProcessLine(QObject):
    signal = pyqtSignal(object)

class RunProcess(QRunnable):
    def __init__(self,*args, path, python_cmd,**kwargs):
        QObject.__init__(self,*args, **kwargs)
        self.signals = ProcessLine()
        self.command = python_cmd
        self.path = path

    @pyqtSlot()
    def run(self):
        self.start()

        # Poll process for new output until finished
        while True:
            nextline = self.read()
            print(nextline)
            if nextline.decode()  == '' and self.process.poll() is not None:
                break
            self.signals.signal.emit(nextline)
    
    def start(self):
        self.process = subprocess.Popen(
            (self.command, self.path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.paused = False


    def read(self):
        nextline = self.process.stdout.readline()
        ansi_escape_8bit = re.compile(
            br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
        )
        result = ansi_escape_8bit.sub(b'', nextline)
        return result
        
        
    def write(self, msg):
        self.process.stdin.write(msg)
        
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
