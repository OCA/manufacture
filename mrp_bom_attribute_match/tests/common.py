from odoo.models import BaseModel
from odoo.tests import Form, SavepointCase


class TestMrpBomAttributeMatchBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.route_manufacture = cls.warehouse.manufacture_pull_id.route_id
        # Create products
        cls.product_sword = cls.env["product.template"].create(
            {
                "name": "Plastic Sword",
                "type": "product",
            }
        )
        cls.product_surf = cls.env["product.template"].create(
            {
                "name": "Surf",
                "type": "product",
            }
        )
        cls.product_fin = cls.env["product.template"].create(
            {
                "name": "Surf Fin",
                "type": "product",
            }
        )
        cls.product_plastic = cls.env["product.template"].create(
            {
                "name": "Plastic Component",
                "type": "product",
            }
        )
        cls.p1 = cls.env["product.template"].create(
            {
                "name": "P1",
                "type": "product",
                "route_ids": [(6, 0, cls.route_manufacture.ids)],
            }
        )
        cls.p2 = cls.env["product.template"].create(
            {
                "name": "P2",
                "type": "product",
                "route_ids": [(6, 0, cls.route_manufacture.ids)],
            }
        )
        cls.p3 = cls.env["product.template"].create(
            {
                "name": "P3",
                "type": "product",
                "route_ids": [(6, 0, cls.route_manufacture.ids)],
            }
        )
        cls.product_9 = cls.env["product.product"].create(
            {
                "name": "Paper",
            }
        )
        cls.product_10 = cls.env["product.product"].create(
            {
                "name": "Stone",
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
                "value_ids": [(6, 0, cls.product_attribute.value_ids.ids)],
            }
        )
        cls.sword_attrs = cls.env["product.template.attribute.line"].create(
            {
                "attribute_id": cls.product_attribute.id,
                "product_tmpl_id": cls.product_sword.id,
                "value_ids": [(6, 0, cls.product_attribute.value_ids.ids)],
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
                    product_id=cls.p1.product_variant_ids[0],
                    product_qty=1,
                ),
            ],
        )

    @classmethod
    def _create_bom(cls, product, line_form_vals):
        if product._name == "product.template":
            template = product
            product = cls.env["product.product"]
        else:
            template = product.product_tmpl_id
        with Form(cls.env["mrp.bom"]) as form:
            form.product_tmpl_id = template
            form.product_id = product
            for vals in line_form_vals:
                with form.bom_line_ids.new() as line_form:
                    for key, value in vals.items():
                        field = line_form._model._fields.get(key)
                        if field and field.relational:  # pragma: no cover
                            if value and not isinstance(value, BaseModel):
                                value = cls.env[field.comodel_name].browse(value)
                            elif not value:
                                value = cls.env[field.comodel_name]
                        setattr(line_form, key, value)
        return form.save()
