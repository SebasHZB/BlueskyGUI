from bluesky import RunEngine
import bluesky.plans as bp
import logging
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import threading
import random
import time
from ophyd.sim import FakeEpicsSignal
from bluesky.callbacks import LivePlot, LiveTable
from bluesky.callbacks.zmq import Proxy
#from bluesky.utils import install_qt_kicker
#install_qt_kicker()

from InjectionBooster import InjectionBooster
from Ophyd_Simulation import Simulation

sim = Simulation()
plt.ion()

RE = RunEngine({})
RE.log.setLevel(logging.INFO)

inj = InjectionBooster(name='booster', signal=sim.signal, motor=sim.motor)
    

fig = plt.figure(figsize=[8,12])
ax_coarse = fig.add_subplot(311)
lp = LivePlot('booster_current', x=inj.offset.name, ax=ax_coarse, marker='.')
    
lt = LiveTable([inj.offset, inj.current])

sim.start()
print('Starting Scan')
RE(bp.scan([inj], inj.offset, 0, 10, 10), [lt, lp])
plt.ioff()
sim.stop()