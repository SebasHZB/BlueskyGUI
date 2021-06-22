#from etc.InjectionBooster import InjectionBooster

from etc.base_plan import Base_Plan

class Custom_Plan(Base_Plan):

    def __init__(self):
        super()#.__init__()

    def describe_devices(self):
        from bact2.ophyd.devices.raw.kicker_offset_v2 import InjectionBooster
        from bact2.ophyd.devices.raw.kicker_offset import InjectionBooster, BoosterCurrent, ForceAboveZero, AverageValue

        self.DEVICES['inj_kicker'] = InjectionBooster(name='booster')
        self.DEVICES['booster_current'] = BoosterCurrent(name='booster_cur')
        self.DEVICES['abvz'] = ForceAboveZero(name='abvz', signal_to_process=self.DEVICES['booster_current'].current)
        self.DEVICES['bca'] = AverageValue(name='bca', signal_to_process=self.DEVICES['booster_current'].current)

        self.NAMES['inj_kicker'] = self.DEVICES['inj_kicker'].offset.name
        self.NAMES['booster_current'] = self.DEVICES['booster_current'].current.name
        self.NAMES['bca'] = self.DEVICES['bca'].mean.name
        

    def describe_plans(self):

        from bluesky import RunEngine
        import bluesky.plans as bp
        from bluesky.callbacks.fitting import PeakStats
        from bact2.ophyd.utils.preprocessors.CounterSink import CounterSink

        b_cur = self.DEVICES['booster_current'].current
        
        cs = CounterSink(name = "cnt_b_cur", delay = .1)

        dep = self.DEVICES['bca'].mean.name
        indep = self.DEVICES['inj_kicker'].offset
        
        md = {
            'nikname' : 'injection_kicker_scan_adaptive'
        }

        start, end = 10.5, 12
        min_step = 0.01
        max_step = 0.05
        min_change = 1

        dets = [ self.DEVICES['inj_kicker'], self.DEVICES['booster_current'], self.DEVICES['abvz'], self.DEVICES['bca'] ]
        
        plan = bp.adaptive_scan(dets, dep, indep, start, end, min_step, max_step, min_change, False, md=md)

        self.PLANS.append(plan)

        start, end = 11, 11.5
        steps = 101

        plan2 = bp.scan(dets, indep, start, end, steps)

        self.PLANS.append(plan2)


    def describe_printers(self):
        from bluesky.callbacks import LiveTable
        
        #markdown table
        table = LiveTable([self.NAMES['inj_kicker'], self.NAMES['booster_current']],
                          out=self.PRINT_CALLBACK)
        self.PRINTERS.append(table)

    def describe_plots(self):
        from bluesky.callbacks import LivePlot
        
        cur_name = self.NAMES['booster_current']
        off_name = self.NAMES['inj_kicker']
        mean_name = self.NAMES['bca']
        self.PLOTS.append(LivePlot(cur_name, x=off_name, ax=self.AXIS[0], marker='.'))
        self.PLOTS.append(LivePlot(mean_name, x=off_name, ax=self.AXIS[1], marker='.'))
