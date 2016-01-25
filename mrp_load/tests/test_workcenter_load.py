from openerp.tests.common import TransactionCase

class ExecuteComputeLoad(TransactionCase):
    def test_compting_load(self):
        workcenter = self.env.ref('mrp.mrp_workcenter_0')
        #We do not support this following options for now
        workcenter.write({
            'time_efficiency': 1,
            'time_start': 0,
            'time_stop': 0,
            'time_cycle': 0})
        intial_load = workcenter.load
        mo = self.env.ref('mrp_load.mrp_production_3')
        mo.signal_workflow('button_confirm')
        mo.force_production()
        self.env['mrp.workcenter'].auto_recompute_load()
        
        
        self.assertEqual(workcenter.load - intial_load, 6)
