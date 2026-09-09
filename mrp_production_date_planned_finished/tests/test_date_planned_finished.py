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

    def test_mrp_production_date_finished_security_lead_not_applied(self):
        """The company security lead time must not shift the requested end date.

        Until v15 the module also subtracted ``company_id.manufacturing_lead``,
        mirroring core, which added it when computing the end date from the
        start one. Since v16 the end date is instead a stored compute
        (``_compute_date_finished``) that only adds ``bom_id.produce_delay``,
        so subtracting the security lead here is immediately undone: core
        recomputes ``date_finished`` from the new ``date_start`` and the order
        ends ``manufacturing_lead`` days before the date the user typed. The
        security lead only applies to procurement now
        (``stock_rule._get_lead_days``), so it must stay out of this onchange.
        """
        self.env.company.manufacturing_lead = 5
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product
        mo_form.bom_id = self.bom
        mo_form.product_qty = 1
        mo_form.date_finished = Datetime.to_datetime("2026-10-10 10:00:00")
        mo = mo_form.save()
        self.assertEqual(
            mo.date_finished,
            Datetime.to_datetime("2026-10-10 10:00:00"),
            "The requested end date must be kept as typed",
        )
        self.assertEqual(
            mo.date_start,
            Datetime.to_datetime("2026-10-08 10:00:00"),
            "Only the BoM lead time must be subtracted from the end date",
        )

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
