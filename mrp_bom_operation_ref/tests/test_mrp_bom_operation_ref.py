# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestMrpWorkcenterCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bom = cls.env.ref("mrp.mrp_bom_manufacture")
        cls.bom_operation = cls.env.ref("mrp.mrp_routing_workcenter_0")
        cls.bom_operation.ref = "MA"

    def test_name_get(self):
        self.assertTrue(self.bom_operation.name_get()[0][1].startswith("[MA] "))
