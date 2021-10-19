#from etc.InjectionBooster import InjectionBooster

from etc.base_plan import Base_Plan

class Custom_Plan(Base_Plan):

    def __init__(self):
        super()#.__init__()

    def describe_devices(self):
        from etc.InjectionBooster import InjectionBooster

        self.DEVICES['inj_kicker'] = InjectionBooster(name='booster')
        
        self.NAMES['offset'] = self.DEVICES['inj_kicker'].offset.name
        self.NAMES['current'] = self.DEVICES['inj_kicker'].current.name

    def describe_plans(self):

        from bluesky import RunEngine
        import bluesky.plans as bp
        from bluesky.callbacks.fitting import PeakStats

        start, end = 10, 13
        min_step = 0.01
        max_step = 0.15
        min_change = 1
        steps = 10

        dets = [ self.DEVICES['inj_kicker'].current, self.DEVICES['inj_kicker'].offset ]
        indep = self.DEVICES['inj_kicker'].offset
        
        plan = bp.scan(dets, indep, start, end, steps)

        self.PLANS.append(plan)

        start, end = 11, 12
        steps = 10

        plan2 = bp.scan(dets, indep, start, end, steps)

        self.PLANS.append(plan2)


    def describe_printers(self):
        from bluesky.callbacks import LiveTable
        
        #markdown table
        table = LiveTable([self.NAMES['offset'], self.NAMES['current']],
                          out=self.PRINT_CALLBACK)
        self.PRINTERS.append(table)

    def describe_plots(self, axes):
        from bluesky.callbacks import LivePlot
        
        cur_name = self.NAMES['current']
        off_name = self.NAMES['offset']
        self.PLOTS.append(LivePlot(cur_name, x=off_name, ax=axes, marker='.'))
