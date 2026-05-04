# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.fields import Datetime
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestDateFinished(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Manufactured Product", "type": "consu", "is_storable": True}
        )
        cls.component = cls.env["product.product"].create(
            {"name": "Test Component", "type": "consu", "is_storable": True}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "produce_delay": 2,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component.id, "product_qty": 1.0}),
                ],
            }
        )

    def test_mrp_production_date_finished_onchange(self):
        """Setting date_finished must back-compute date_start using BoM lead time."""
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1
        mo_form.date_finished = Datetime.to_datetime("2026-10-10 10:00:00")
        mo = mo_form.save()
        self.assertEqual(mo.date_start, Datetime.to_datetime("2026-10-08 10:00:00"))
        self.assertEqual(mo.date_finished, Datetime.to_datetime("2026-10-10 10:00:00"))

    def test_mrp_production_date_finished_decoration(self):
        """date_finished decorations must mirror date_start ones.

        If a future Odoo update changes the decorations on date_start, this
        test will fail to flag the mismatch so the inheritance can be updated.
        """
        view = self.env["mrp.production"].get_view(view_type="form")
        doc = etree.XML(view["arch"])
        date_start = doc.xpath("//field[@name='date_start']")[0]
        # The form has two `date_finished` fields (one technical hidden); pick
        # the visible one inside group_extra_info.
        date_finished = doc.xpath(
            "//group[@name='group_extra_info']/field[@name='date_finished']"
        )[0]
        decoration_attrs = [
            attr for attr in date_start.attrib if attr.startswith("decoration-")
        ]
        self.assertTrue(decoration_attrs, "date_start has no decorations to mirror")
        for attr in decoration_attrs:
            self.assertEqual(
                date_start.attrib[attr],
                date_finished.attrib.get(attr),
                f"date_finished decoration mismatch: {attr}",
            )
