# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo.fields import Datetime as Dt
from odoo.tests import Form

from odoo.addons.mrp.tests import common


class TestMrpDefaultWorkorderTime(common.TestMrpCommon):
    def _crete_production_with_workorders(self, product_qty=100):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.bom_2.product_id
        mo_form.bom_id = self.bom_2
        mo_form.product_qty = product_qty
        mo = mo_form.save()
        self.env["stock.quant"]._update_available_quantity(
            self.product_4, self.stock_location, 200
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product_3, self.stock_location, 200
        )
        mo.date_planned_start = Dt.now()
        mo.action_confirm()
        mo.action_assign()
        mo.button_plan()
        return mo

    def test_mrp_default_workorder_time(self):
        self.stock_location = self.env.ref("stock.stock_location_stock")
        fully_productive_time = self.env["mrp.workcenter.productivity.loss"].search(
            [("loss_type", "=", "performance")], limit=1
        )
        mo = self._crete_production_with_workorders(1)
        self.assertEqual(len(mo), 1, "MO should have been created")
        mo.button_mark_done()
        self.assertEqual(
            mo.workorder_ids[0].duration, mo.workorder_ids[0].duration_expected
        )

        mo2 = self._crete_production_with_workorders(1)
        mo2.company_id.use_projected_time_work_orders = False
        self.assertEqual(len(mo2), 1, "MO should have been created")
        mo2.button_mark_done()
        self.assertNotEqual(
            mo2.workorder_ids[0].duration, mo2.workorder_ids[0].duration_expected
        )

        mo3 = self._crete_production_with_workorders(1)
        mo3.company_id.use_projected_time_work_orders = True
        mo3.company_id.minimum_order_time_threshold = 20
        self.assertEqual(len(mo3), 1, "MO should have been created")
        date_start = Dt.now()
        date_end = date_start + relativedelta(
            minutes=mo3.workorder_ids[0].duration_expected
            * (mo3.company_id.minimum_order_time_threshold / 100.0)
        )
        mo3.workorder_ids.write(
            {
                "time_ids": [
                    (
                        0,
                        0,
                        {
                            "user_id": self.env.user.id,
                            "date_start": date_start,
                            "date_end": date_end,
                            "loss_id": fully_productive_time.id,
                            "workcenter_id": mo3.workorder_ids[0].workcenter_id.id,
                            "description": fully_productive_time.name,
                        },
                    )
                ]
            }
        )
        mo3.button_mark_done()
        self.assertEqual(
            mo3.workorder_ids[0].duration, mo3.workorder_ids[0].duration_expected
        )

        mo4 = self._crete_production_with_workorders(1)
        mo4.company_id.use_projected_time_work_orders = True
        mo4.company_id.minimum_order_time_threshold = 20
        self.assertEqual(len(mo4), 1, "MO should have been created")
        date_start = Dt.now()
        date_end = date_start + relativedelta(
            minutes=mo4.workorder_ids[0].duration_expected
            * ((mo4.company_id.minimum_order_time_threshold + 1) / 100.0)
        )
        mo4.workorder_ids.write(
            {
                "time_ids": [
                    (
                        0,
                        0,
                        {
                            "user_id": self.env.user.id,
                            "date_start": date_start,
                            "date_end": date_end,
                            "loss_id": fully_productive_time.id,
                            "workcenter_id": mo4.workorder_ids[0].workcenter_id.id,
                            "description": fully_productive_time.name,
                        },
                    )
                ]
            }
        )
        mo4.button_mark_done()
        self.assertNotEqual(
            mo4.workorder_ids[0].duration, mo4.workorder_ids[0].duration_expected
        )
