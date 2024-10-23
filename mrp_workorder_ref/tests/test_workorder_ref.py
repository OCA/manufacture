# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestMrpWorkcenterCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bom_operation = cls.env.ref("mrp.mrp_routing_workcenter_0")
        cls.bom_operation.ref = "MA"
        cls.bom = cls.bom_operation.bom_id
        cls.product_tmpl = cls.bom.product_tmpl_id
        cls.product = cls.product_tmpl.product_variant_ids[0]

    def test_routing_name_get(self):
        self.assertTrue(self.bom_operation.name_get()[0][1].startswith("[MA] "))

    def test_workorder_name_get(self):
        wo = self.env["mrp.workorder"].search([], limit=1)
        wo.ref = "MA"
        self.assertTrue(wo.name_get()[0][1].startswith("[MA] "))

    def test_create_mo(self):
        with Form(self.env["mrp.production"]) as form:
            form.product_id = self.product
            form.bom_id = self.bom
        mo = form.save()
        wo = mo.workorder_ids.filtered(lambda r: r.operation_id == self.bom_operation)
        self.assertEqual(
            wo.ref, self.bom_operation.ref, "Workorder copied from BoM operation"
        )
