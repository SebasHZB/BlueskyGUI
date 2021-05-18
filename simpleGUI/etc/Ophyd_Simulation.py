import threading
import random
import time
from ophyd.sim import FakeEpicsSignal

class Simulation():
    
    def __init__(self):
        self.signal = FakeEpicsSignal('rdCurrentB', name='curr')
        self.motor = FakeEpicsSignal('MRC25V', name='motor')
        self.motor.value = 0.0
        self.scanRunning = True
        
    def set_signal(self, *args):
        while self.scanRunning:
            self.signal.put(random.random())
            time.sleep(1)
            
            
    def start(self):
        p = threading.Thread(target=self.set_signal)
        p.start()
    
    def stop(self):
        self.scanRunning = False

        
if __name__ == '__main__':
    sim = Simulation()
    print(sim.motor.get())
    sim.start()
    for i in range(10):
        print(sim.signal.get())
        time.sleep(1)
    sim.stop()