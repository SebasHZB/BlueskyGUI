#from etc.InjectionBooster import InjectionBooster

from etc.base_plan import Base_Plan

class Custom_Plan(Base_Plan):

    def __init__(self):
        super()#.__init__()

    def describe_devices(self):
        from bact2.ophyd.devices.raw.kicker import Delay
        from bact2.ophyd.devices.raw.booster_current import BoosterCurrentCollection

        self.DEVICES['inj_kicker'] = Delay('KIWB', name='ik')
        self.DEVICES['booster_current'] = BoosterCurrentCollection(name='cs')

        self.NAMES['inj_kicker'] = self.DEVICES['inj_kicker'].offset.name
        self.NAMES['booster_current1'] = self.DEVICES['booster_current'].cur1.current.name
        self.NAMES['booster_current2'] = self.DEVICES['booster_current'].cur2.current.name


    def describe_plans(self):

        from bluesky import RunEngine
        import bluesky.plans as bp
        from bluesky.callbacks.fitting import PeakStats
        from bact2.ophyd.utils.preprocessors.CounterSink import CounterSink

        cs = CounterSink(name = "cnt_b_cur", delay = .1)

        dep =  self.DEVICES['booster_current'].cur1.current
        indep = self.DEVICES['inj_kicker'].offset

        md = {
            'nickname' : 'injection_kicker_scan_adaptive'
        }

        start, end = 10.5, 12
        min_step = 0.01
        max_step = 0.05
        min_change = 1

        dets = [indep, dep, self.DEVICES['booster_current']]

        plan = bp.adaptive_scan(dets, dep, indep, start, end, min_step, max_step, min_change, False, md=md)

        self.PLANS.append(plan)

        start, end = 11, 11.5
        steps = 101

        plan2 = bp.scan(dets, indep, start, end, steps)
        self.PLANS.append(plan2)

    def describe_printers(self):
        from bluesky.callbacks import LiveTable

        #markdown table
        table = LiveTable([self.NAMES['inj_kicker'], self.NAMES['booster_current1'],  self.NAMES['booster_current2']],
                          out=self.PRINT_CALLBACK)
        self.PRINTERS.append(table)

    def describe_plots(self):
        from bluesky.callbacks import LivePlot

        off_name = self.NAMES['inj_kicker']

        cur1_name = self.NAMES['booster_current1']
        cur2_name = self.NAMES['booster_current2']
        self.PLOTS.append(LivePlot(cur1_name, x=off_name, ax=self.AXIS[0], marker='.'))
        self.PLOTS.append(LivePlot(cur2_name, x=off_name, ax=self.AXIS[1], marker='.'))
