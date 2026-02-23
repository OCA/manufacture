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

        # Create products
        cls.product_sword = cls.env["product.template"].create(
            {"name": "Plastic Sword", "type": "consu"}
        )
        cls.product_surf = cls.env["product.template"].create(
            {"name": "Surf", "type": "consu"}
        )
        cls.product_fin = cls.env["product.template"].create(
            {"name": "Surf Fin", "type": "consu"}
        )
        cls.product_plastic = cls.env["product.template"].create(
            {"name": "Plastic Component", "type": "consu"}
        )
        cls.p1 = cls.env["product.template"].create(
            {
                "name": "P1",
                "type": "consu",
                "route_ids": [Command.link(cls.route_manufacture.id)],
            }
        )
        cls.p2 = cls.env["product.template"].create(
            {
                "name": "P2",
                "type": "consu",
                "route_ids": [Command.link(cls.route_manufacture.id)],
            }
        )
        cls.p3 = cls.env["product.template"].create(
            {
                "name": "P3",
                "type": "consu",
                "route_ids": [Command.link(cls.route_manufacture.id)],
            }
        )

        cls.product_9 = cls.env["product.product"].create(
            {"name": "Paper", "type": "consu"}
        )
        cls.product_10 = cls.env["product.product"].create(
            {"name": "Stone", "type": "consu"}
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
                "value_ids": [Command.set(cls.attribute_value_ids.ids)],
            }
        )
        cls.sword_attrs = cls.env["product.template.attribute.line"].create(
            {
                "attribute_id": cls.product_attribute.id,
                "product_tmpl_id": cls.product_sword.id,
                "value_ids": [Command.set(cls.attribute_value_ids.ids)],
            }
        )

        cls.env.ref("uom.group_uom").write(
            {"user_ids": [Command.link(cls.env.user.id)]}
        )

        # Fix E501: Multi-line formatting for BoM creation
        cls.bom_id = cls._create_bom(
            cls.product_sword,
            [
                {"component_template_id": cls.product_plastic.id, "product_qty": 1},
                {"product_id": cls.product_9.id, "product_qty": 1},
            ],
        )

        # Get first variant ID for plastic to avoid long lines
        plastic_v1 = cls.product_plastic.product_variant_ids[0].id
        cls.fin_bom_id = cls._create_bom(
            cls.product_fin,
            [{"product_id": plastic_v1, "product_qty": 1}],
        )

        fin_v1 = cls.product_fin.product_variant_ids[0].id
        cls.surf_bom_id = cls._create_bom(
            cls.product_surf,
            [{"product_id": fin_v1, "product_qty": 1}],
        )

        p2_v1 = cls.p2.product_variant_ids[0].id
        cls.p1_bom_id = cls._create_bom(
            cls.p1,
            [{"product_id": p2_v1, "product_qty": 1}],
        )

        p3_v1 = cls.p3.product_variant_ids[0].id
        cls.p2_bom_id = cls._create_bom(
            cls.p2,
            [{"product_id": p3_v1, "product_qty": 1}],
        )

        sword_v2 = cls.product_sword.product_variant_ids[1].id
        cls.p3_bom_id = cls._create_bom(
            cls.p3,
            [{"product_id": sword_v2, "product_qty": 1}],
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
                    if value and isinstance(value, BaseModel):
                        value = value.id
                    elif value and isinstance(value, (list, tuple)) and value:
                        # Fix E501
                        first_val = value[0]
                        if isinstance(first_val, BaseModel):
                            value = first_val.id
                        else:
                            value = first_val
                line_vals[key] = value

            bom_vals["bom_line_ids"].append(Command.create(line_vals))

        return cls.env["mrp.bom"].create(bom_vals)
