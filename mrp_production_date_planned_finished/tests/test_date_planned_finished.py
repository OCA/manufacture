# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import Form, TransactionCase


class TestDatePlannedFinished(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.company.manufacturing_lead = 1
        cls.product = cls.env.ref("mrp.product_product_computer_desk")
        cls.product.produce_delay = 1
        cls.product_bom = cls.env.ref("mrp.mrp_bom_desk")

    def test_mrp_production_date_planned_finished_onchange(self):
        """Test that date_planned_start is set when date_planned_finished is changed."""
        with Form(self.env["mrp.production"]) as mo:
            mo.product_id = self.product
            mo.bom_id = self.product_bom
            mo.product_qty = 1
            mo.date_planned_finished = "2022-10-10 10:00:00"
        self.assertEqual(mo.date_planned_start, "2022-10-08 10:00:00")

    def test_mrp_production_date_planned_finished_decoration(self):
        """Test that the date_planned_finished field is decorated properly

        Its decoration has to exactly match the date_planned_start one.
        As this might change if odoo updates their code, or during migrations,
        this test case will track any mismatches and fail.
        """
        res = self.env["mrp.production"].fields_view_get(view_type="form")
        doc = etree.XML(res["arch"])
        date_planned_start = doc.xpath("//field[@name='date_planned_start']")[0]
        date_planned_finished = doc.xpath("//field[@name='date_planned_finished']")[0]
        decoration_attrs = [
            attr
            for attr in date_planned_start.attrib.keys()
            if attr.startswith("decoration-")
        ]
        for attr in decoration_attrs:
            self.assertEqual(
                date_planned_start.attrib[attr],
                date_planned_finished.attrib[attr],
                f"date_planned_finished decoration mismatch: {attr}",
            )
