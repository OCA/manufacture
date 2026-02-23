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

        # Create products - Odoo 19 uses 'detailed_type' instead of 'type'
        cls.product_sword = cls.env["product.template"].create(
            {
                "name": "Plastic Sword",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )
        cls.product_surf = cls.env["product.template"].create(
            {
                "name": "Surf",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )
        cls.product_fin = cls.env["product.template"].create(
            {
                "name": "Surf Fin",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )
        cls.product_plastic = cls.env["product.template"].create(
            {
                "name": "Plastic Component",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )
        cls.p1 = cls.env["product.template"].create(
            {
                "name": "P1",
                "detailed_type": "product",  # Changed for Odoo 19
                "route_ids": [Command.link(cls.route_manufacture.id)],
            }
        )
        cls.p2 = cls.env["product.template"].create(
            {
                "name": "P2",
                "detailed_type": "product",  # Changed for Odoo 19
                "route_ids": [Command.link(cls.route_manufacture.id)],
            }
        )
        cls.p3 = cls.env["product.template"].create(
            {
                "name": "P3",
                "detailed_type": "product",  # Changed for Odoo 19
                "route_ids": [Command.link(cls.route_manufacture.id)],
            }
        )
        cls.product_9 = cls.env["product.product"].create(
            {
                "name": "Paper",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )
        cls.product_10 = cls.env["product.product"].create(
            {
                "name": "Stone",
                "detailed_type": "product",  # Changed for Odoo 19
            }
        )
        cls.product_attribute = cls.env["product.attribute"].create(
            {"name": "Colour", "display_type": "radio", "create_variant": "always"}
        )
        cls.attribute_value_ids = cls.env["product.attribute.value"].create(
            [
                {"name": "Cyan", "attribute_id": cls.product_attribute.id},
                {"name": "Magenta", "attribute_id": cls.product_attribute.id},
            ]
        )
        cls.plastic_attrs = cls.env["product.template.attribute.line"].create(
            {
                "attribute_id": cls.product_attribute.id,
                "product_tmpl_id": cls.product_plastic.id,
                "value_ids": [Command.set(cls.product_attribute.value_ids.ids)],
            }
        )
        cls.sword_attrs = cls.env["product.template.attribute.line"].create(
            {
                "attribute_id": cls.product_attribute.id,
                "product_tmpl_id": cls.product_sword.id,
                "value_ids": [Command.set(cls.product_attribute.value_ids.ids)],
            }
        )
        cls.env.ref("uom.group_uom").write(
            {
                "user_ids": [
                    Command.link(cls.env.user.id),
                ],
            }
        )
        # Create boms
        cls.bom_id = cls._create_bom(
            cls.product_sword,
            [
                dict(
                    component_template_id=cls.product_plastic.id,
                    product_qty=1,
                ),
                dict(
                    product_id=cls.product_9,
                    product_qty=1,
                ),
            ],
        )
        cls.fin_bom_id = cls._create_bom(
            cls.product_fin,
            [
                dict(
                    product_id=cls.product_plastic.product_variant_ids[0],
                    product_qty=1,
                ),
            ],
        )
        cls.surf_bom_id = cls._create_bom(
            cls.product_surf,
            [
                dict(
                    product_id=cls.product_fin.product_variant_ids[0],
                    product_qty=1,
                ),
            ],
        )
        cls.p1_bom_id = cls._create_bom(
            cls.p1,
            [
                dict(
                    product_id=cls.p2.product_variant_ids[0],
                    product_qty=1,
                ),
            ],
        )
        cls.p2_bom_id = cls._create_bom(
            cls.p2,
            [
                dict(
                    product_id=cls.p3.product_variant_ids[0],
                    product_qty=1,
                ),
            ],
        )
        cls.p3_bom_id = cls._create_bom(
            cls.p3,
            [
                dict(
                    product_id=cls.product_sword.product_variant_ids[1],
                    product_qty=1,
                ),
            ],
        )

    @classmethod
    def _create_bom(cls, product, line_form_vals):
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
                    if value and not isinstance(value, BaseModel):
                        value = cls.env[field.comodel_name].browse(value)
                    if value:
                        value = value.id
                    else:
                        value = False
                line_vals[key] = value

            bom_vals["bom_line_ids"].append((0, 0, line_vals))

        return cls.env["mrp.bom"].create(bom_vals)
