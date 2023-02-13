# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, TransactionCase


class TestMrpLotProductionDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_table_top")  # Tracked by S/N

    @classmethod
    def _create_manufacturing_order(cls, bom, product_qty=1):
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = bom
            form.product_qty = product_qty
            order = form.save()
            order.invalidate_recordset()
            return order

    @classmethod
    def _validate_manufacturing_order(cls, order):
        order.action_confirm()
        order.action_assign()
        # To ease the test we generate the lot manually, but this could be
        # handled automatically by calling the 'Immediate production' wizard
        order.action_generate_serial()
        order.button_mark_done()

    def test_lot_production_date(self):
        order = self._create_manufacturing_order(self.bom)
        self._validate_manufacturing_order(order)
        self.assertTrue(order.lot_producing_id.production_date)
