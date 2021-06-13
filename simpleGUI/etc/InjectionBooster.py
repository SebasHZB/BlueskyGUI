from ophyd.status import SubscriptionStatus
from ophyd import Device, EpicsSignal, EpicsSignalRO, Signal
from ophyd import Component as Cpt, Kind
import random
import time

class InjectionBooster(Device):
    current = Cpt(Signal, name='curr')
    offset = Cpt(Signal, name='motor')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_current(0.0)
        self.set_offset(0.0)
        self.offset.subscribe(self.simulation)
        
    def set_current(self, value, **kwargs):
        self.current.put(value)
        
    def set_offset(self, value, **kwargs):
        self.offset.put(value)

    def simulation(self, *args, **kwargs):
        time.sleep(1)
        self.set_current(random.random())
    
    def trigger(self):
        def check_value(old_value, value, **kwargs):
            dif = abs(old_value - value)
            return dif > 0

        stat = SubscriptionStatus(self.current, check_value, run=False)
        return stat
    
    
if __name__ == '__main__':
    import bluesky.plans as bp
    from bluesky import RunEngine
    from ophyd.sim import FakeEpicsSignal
    
    testsignal = FakeEpicsSignal('rdCurrentB', name='curr')
    test_motor = FakeEpicsSignal('MRC25V', name='motor')
    test_motor.value = 0.0
    
    RE = RunEngine({})
    RE.subscribe(print)
    device = InjectionBooster(name='inj_booster')
    RE(bp.scan([device.current], device.offset, 0, 10, 10))
    print('done')