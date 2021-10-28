from etc.base_plan import Base_Plan

class Custom_Plan(Base_Plan):

    def __init__(self):
        super()

    def describe_devices(self):
        from bessyii_devices.keithley import Keithley6514, Keithley6517
        from ophyd.sim import motor

        self.DEVICES['kth01'] = Keithley6517('AQUARIUSEL:' + 'Keithley00:',  name='Keithley00', read_attrs=['readback'])
        self.DEVICES['kth02'] = Keithley6514('AQUARIUSEL:' + 'Keithley01:',  name='Keithley01', read_attrs=['readback'])
        #self.DEVICES['motor'] = motor

        self.NAMES['kth01'] = self.DEVICES['kth01'].readback.name
        self.NAMES['kth02'] = self.DEVICES['kth02'].readback.name
        #self.NAMES['motor'] = self.DEVICES['motor'].name

    def describe_plans(self):

        from bluesky import RunEngine
        import bluesky.plans as bp

        kth01 = self.DEVICES['kth01']
        kth02 = self.DEVICES['kth02']
        #motor = self.DEVICES['motor']

        plan1 = bp.count([kth01], 20)

        plan2 = bp.count([kth02], 20)
        
        #plan1 = bp.scan([kth01], motor, 0, 10, 11)

        #plan2 = bp.scan([kth02], motor, 0, 10, 11)

        self.PLANS.append(plan1)
        self.PLANS.append(plan2)


    def describe_printers(self, cb):
        from bluesky.callbacks import LiveTable

        table1 = LiveTable([self.NAMES['kth01'], self.NAMES['kth02']], out=cb)
        self.PRINTERS.append(table1)

    def describe_plots(self, axes):
        from bluesky.callbacks.mpl_plotting import LivePlot, LiveGrid
        
        kth01 = self.NAMES['kth01']
        kth02 = self.NAMES['kth02']
        #motor = self.NAMES['motor']
        self.PLOTS.append(LivePlot(kth01, ax=axes))
        self.PLOTS.append(LivePlot(kth02, ax=axes))
        #self.PLOTS.append(LivePlot(kth01, x=motor, ax=axes))
        #self.PLOTS.append(LivePlot(kth02, x=motor, ax=axes))

        #self.PLOTS.append(LiveGrid((11, 11), det, ax=axes))
