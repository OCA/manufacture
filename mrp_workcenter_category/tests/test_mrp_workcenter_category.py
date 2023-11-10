# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestMrpWorkcenterCategory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.categ_extrusion = cls.env.ref("mrp_workcenter_category.categ_extrusion")
        cls.categ_pp = cls.env.ref("mrp_workcenter_category.categ_extrusion_pp")
        cls.categ_pvc = cls.env.ref("mrp_workcenter_category.categ_extrusion_pvc")

    def test_complete_name(self):
        self.assertEqual(self.categ_pp.complete_name, "Extrusion / Polypropylene")

    def test_check_recursion(self):
        with self.assertRaisesRegex(UserError, "Recursion Detected"):
            self.categ_extrusion.parent_id = self.categ_pvc

    def test_name_create(self):
        record_id, __ = self.env["mrp.workcenter.category"].name_create("Test")
        record = self.env["mrp.workcenter.category"].browse(record_id)
        self.assertEqual(record.name, "Test")
