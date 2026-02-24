# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import Command
from odoo.models import BaseModel
from odoo.tests.common import TransactionCase


class TestMrpBomAttributeMatchBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.route_manufacture = cls.warehouse.manufacture_pull_id.route_id

        cls.product_attribute = cls.env["product.attribute"].create(
            {
                "name": "Colour",
                "display_type": "radio",
                "create_variant": "always",
            }
        )
        cls.attribute_value_ids = cls.env["product.attribute.value"].create(
            [
                {"name": "Cyan", "attribute_id": cls.product_attribute.id},
                {"name": "Magenta", "attribute_id": cls.product_attribute.id},
            ]
        )

        cls.product_9 = cls.env["product.product"].create(
            {
                "name": "Paper",
                "type": "consu",
            }
        )
        cls.product_10 = cls.env["product.product"].create(
            {
                "name": "Stone",
                "type": "consu",
            }
        )

        cls.product_sword = cls.env["product.template"].create(
            {
                "name": "Plastic Sword",
                "type": "consu",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.product_attribute.id,
                            "value_ids": [Command.set(cls.attribute_value_ids.ids)],
                        }
                    )
                ],
            }
        )

    @classmethod
    def _create_bom(cls, product, line_form_vals):
        """Helper to create BoMs while covering all logic branches."""
        if product._name == "product.template":
            template = product
            product_variant = product.product_variant_id
        else:
            template = product.product_tmpl_id
            product_variant = product
        bom_vals = {
            "product_tmpl_id": template.id,
            "product_id": product_variant.id,
            "product_qty": 1.0,
            "type": "normal",
            "bom_line_ids": [],
        }
        for vals in line_form_vals:
            line_vals = {}
            for key, value in vals.items():
                field = cls.env["mrp.bom.line"]._fields.get(key)
                if field and field.relational:
                    if value and isinstance(value, BaseModel):
                        value = value.id
                    elif value and isinstance(value, (list, tuple)):
                        first_val = value[0]
                        if isinstance(first_val, BaseModel):
                            value = first_val.id
                        else:
                            value = first_val
                line_vals[key] = value
            bom_vals["bom_line_ids"].append(Command.create(line_vals))

        return cls.env["mrp.bom"].create(bom_vals)
