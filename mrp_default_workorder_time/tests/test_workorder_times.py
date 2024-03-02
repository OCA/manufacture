# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo.fields import Datetime as Dt
from odoo.tests import Form

from odoo.addons.mrp.tests import common


class TestMrpDefaultWorkorderTime(common.TestMrpCommon):
    def _crete_production_with_workorders(
        self, product_qty=100, set_time=False, percent_time=False
    ):
        fully_productive_time = self.env["mrp.workcenter.productivity.loss"].search(
            [("loss_type", "=", "performance")], limit=1
        )
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
        if set_time:
            date_start = Dt.now()
            date_end = date_start + relativedelta(
                minutes=mo.workorder_ids[0].duration_expected * (percent_time / 100.0)
            )
            mo.workorder_ids.write(
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
                                "workcenter_id": mo.workorder_ids[0].workcenter_id.id,
                                "description": fully_productive_time.name,
                            },
                        )
                    ]
                }
            )
        return mo

    def finish_production(self, mo):
        res = mo.button_mark_done()
        if res is not True:
            ctx = {
                "active_id": mo.id,
                "active_ids": mo.ids,
                "active_model": "mrp.production",
            }
            ctx.update(res.get("context", {}))
            wizard_form = Form(self.env["mrp.immediate.production"].with_context(**ctx))
            wizard = wizard_form.save()
            if mo.company_id.use_projected_time_work_orders:
                wizard.process()

    def test_mrp_default_workorder_time(self):
        self.stock_location = self.env.ref("stock.stock_location_stock")
        mo = self._crete_production_with_workorders(1)
        self.assertEqual(len(mo), 1, "MO should have been created")
        self.finish_production(mo)
        self.assertEqual(
            mo.workorder_ids[0].duration, mo.workorder_ids[0].duration_expected
        )

        mo2 = self._crete_production_with_workorders(1)
        mo2.company_id.use_projected_time_work_orders = False
        self.assertEqual(len(mo2), 1, "MO should have been created")
        self.finish_production(mo2)
        self.assertNotEqual(
            mo2.workorder_ids[0].duration, mo2.workorder_ids[0].duration_expected
        )

        mo3 = self._crete_production_with_workorders(
            1, True, mo.company_id.minimum_order_time_threshold
        )
        mo3.company_id.use_projected_time_work_orders = True
        mo3.company_id.minimum_order_time_threshold = 20
        self.assertEqual(len(mo3), 1, "MO should have been created")
        self.finish_production(mo3)
        self.assertEqual(
            mo3.workorder_ids[0].duration, mo3.workorder_ids[0].duration_expected
        )

        mo4 = self._crete_production_with_workorders(
            1, True, mo.company_id.minimum_order_time_threshold + 1
        )
        mo4.company_id.use_projected_time_work_orders = True
        mo4.company_id.minimum_order_time_threshold = 20
        self.assertEqual(len(mo4), 1, "MO should have been created")
        self.finish_production(mo4)
        self.assertNotEqual(
            mo4.workorder_ids[0].duration, mo4.workorder_ids[0].duration_expected
        )

        mo5 = self._crete_production_with_workorders(
            1, True, mo.company_id.maximum_order_time_threshold
        )
        mo5.company_id.use_projected_time_work_orders = True
        mo5.company_id.minimum_order_time_threshold = 20
        self.assertEqual(len(mo5), 1, "MO should have been created")
        self.finish_production(mo5)
        self.assertNotEqual(
            mo5.workorder_ids[0].duration, mo5.workorder_ids[0].duration_expected
        )

        mo6 = self._crete_production_with_workorders(
            1, True, mo.company_id.maximum_order_time_threshold + 1
        )
        mo6.company_id.use_projected_time_work_orders = True
        mo6.company_id.minimum_order_time_threshold = 20
        self.assertEqual(len(mo6), 1, "MO should have been created")
        self.finish_production(mo6)
        self.assertNotEqual(
            mo6.workorder_ids[0].duration, mo6.workorder_ids[0].duration_expected
        )
