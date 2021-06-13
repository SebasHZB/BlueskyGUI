from bluesky.plan_stubs import checkpoint, abs_set, trigger_and_read
import bluesky.plans as bp
from bluesky.callbacks import LivePlot, LiveTable

from etc.InjectionBooster import InjectionBooster
from etc.base_plan import Base_Plan

from ophyd.sim import FakeEpicsSignal


class Custom_Plan(Base_Plan):
    
    def __init__(self):
        super()
    
    def describe_devices(self):
        self.DEVICES['Injection_Booster'] = InjectionBooster(name='booster')
        
    def describe_plans(self):
        self.PLANS.append(custom_scan([self.DEVICES['Injection_Booster'].current], self.DEVICES['Injection_Booster'].offset, 
                                             0, 10, 10))
        
    def describe_printers(self):
        table = LiveTable([self.DEVICES['Injection_Booster'].offset, self.DEVICES['Injection_Booster'].current],
                          out=self.PRINT_CALLBACK)
        self.PRINTERS.append(table)
        
    def describe_plots(self, axis):      
        cur_name = self.DEVICES['Injection_Booster'].current.name
        off_name = self.DEVICES['Injection_Booster'].offset.name
        self.PLOTS.append(LivePlot(cur_name, x=off_name, ax=axis, marker='.'))

def custom_step(detectors, motor, step):
    """
    Inner loop of a 1D step scan

    This is the default function for ``per_step`` param in 1D plans.
    """
    yield from checkpoint()
    yield from abs_set(motor, step, wait=True)
    return (yield from trigger_and_read(list(detectors) + [motor]))

def custom_scan(detectors, motor, start, stop, step):
    yield from bp.scan(detectors, motor, start, stop, step)
    
def custom_plan(sim):
    device = InjectionBooster(name='booster', signal=sim.signal, motor=sim.motor)
    yield from bp.scan([device], device.offset, 0, 10, 10)
    
    
    
    
if __name__ == '__main__':
    from bluesky import RunEngine
    sim = Simulation()
    RE = RunEngine({})
    RE.subscribe(print)
    
    sim.start()
    
    plan = custom_plan(sim)
    RE(plan)
    sim.stop()
    