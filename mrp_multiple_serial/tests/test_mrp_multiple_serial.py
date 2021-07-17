# Copyright 2022 Le Filament
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpSaleInfo(TestMrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_mrp_multiple_serial(self):
        mo = self.generate_mo(tracking_final="serial")[0]
        mo.create_multi = True
        mo.action_generate_serials()
        self.assertEqual(mo.generated_serials, 5)
        self.assertEqual(len(mo.generated_serials_ids), 5)
        self.assertEqual(mo.qty_producing, 5)
        mo.button_mark_done()
        self.assertEqual(mo.qty_produced, 5)

    def test_mrp_single_serial(self):
        mo = self.generate_mo(tracking_final="serial", qty_final=1)[0]
        mo.action_generate_serial()
        self.assertEqual(mo.generated_serials, 0)
        self.assertEqual(len(mo.generated_serials_ids), 0)
        self.assertEqual(mo.qty_producing, 1)
        mo.button_mark_done()
        self.assertEqual(mo.qty_produced, 1)
