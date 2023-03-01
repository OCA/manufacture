# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class CommonCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Create bom, product and components
        cls.component = cls.env["product.product"].create(
            {
                "name": "Component",
                "detailed_type": "product",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "detailed_type": "product",
                "tracking": "lot",
            }
        )
        cls.product_bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": cls.product.uom_id.id,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.component.uom_id.id,
                        }
                    )
                ],
            }
        )
        # Create some initial stocks
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].create(
            {
                "product_id": cls.component.id,
                "product_uom_id": cls.component.uom_id.id,
                "location_id": cls.location_stock.id,
                "quantity": 10.00,
            }
        )
        # Create the MO
        cls.production = cls._create_mrp_production(
            product=cls.product,
            bom=cls.product_bom,
        )

    @classmethod
    def _create_mrp_production(
        cls, product=None, bom=None, quantity=5.0, confirm=False
    ):
        if product is None:  # pragma: no cover
            product = cls.product
        if bom is None:  # pragma: no cover
            bom = cls.product_bom
        mo_form = Form(cls.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = quantity
        mo_form.product_uom_id = product.uom_id
        mo = mo_form.save()
        if confirm:  # pragma: no cover
            mo.action_confirm()
        return mo

    def _mrp_production_set_quantity_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.qty_done = line.product_uom_qty
        order.move_raw_ids._recompute_state()
        order.qty_producing = order.product_qty

    def _mrp_production_split(self, order, **vals):
        action = order.action_split()
        Wizard = self.env[action["res_model"]]
        Wizard = Wizard.with_context(active_model=order._name, active_id=order.id)
        Wizard = Wizard.with_context(**action["context"])
        wizard = Wizard.create(vals)
        res = wizard.apply()
        records = self.env[res["res_model"]].search(res["domain"])
        return records
