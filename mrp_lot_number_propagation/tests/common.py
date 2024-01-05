# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import random
import string

from odoo import fields
from odoo.tests import Form, common


class Common(common.TransactionCase):

    LOT_NAME = "PROPAGATED-LOT"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_desk")
        cls.bom_product_template = cls.env.ref(
            "mrp.product_product_computer_desk_product_template"
        )
        cls.bom_product_product = cls.env.ref("mrp.product_product_computer_desk")
        cls.product_tracked_by_lot = cls.env.ref(
            "mrp.product_product_computer_desk_leg"
        )
        cls.product_tracked_by_sn = cls.env.ref(
            "mrp.product_product_computer_desk_head"
        )
        cls.product_template_tracked_by_sn = cls.env.ref(
            "mrp.product_product_computer_desk_head_product_template"
        )
        cls.line_tracked_by_lot = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id == cls.product_tracked_by_lot
        )
        cls.line_tracked_by_sn = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id == cls.product_tracked_by_sn
        )
        cls.line_no_tracking = fields.first(
            cls.bom.bom_line_ids.filtered(lambda o: o.product_id.tracking == "none")
        )

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None, in_date=None
    ):
        quants = cls.env["stock.quant"]._gather(
            product, location, lot_id=lot, package_id=package, strict=True
        )
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(
            product,
            location,
            quantity,
            package_id=package,
            lot_id=lot,
            in_date=in_date,
        )

    @classmethod
    def _update_stock_component_qty(cls, order=None, bom=None, location=None):
        if not order and not bom:
            return
        if order:
            bom = order.bom_id
        if not location:
            location = cls.env.ref("stock.stock_location_stock")
        for line in bom.bom_line_ids:
            if line.product_id.type != "product":
                continue
            lot = None
            if line.product_id.tracking != "none":
                lot_name = "".join(
                    random.choice(string.ascii_lowercase) for i in range(10)
                )
                if line.propagate_lot_number:
                    lot_name = cls.LOT_NAME
                vals = {
                    "product_id": line.product_id.id,
                    "company_id": line.company_id.id,
                    "name": lot_name,
                }
                lot = cls.env["stock.production.lot"].create(vals)
            cls._update_qty_in_location(
                location,
                line.product_id,
                line.product_qty,
                lot=lot,
            )

    @classmethod
    def _get_lot_quants(cls, lot, location=None):
        quants = lot.quant_ids.filtered(lambda q: q.quantity > 0)
        if location:
            quants = quants.filtered(
                lambda q: q.location_id.parent_path in location.parent_path
            )
        return quants

    @classmethod
    def _add_color_and_legs_variants(cls, product_template):
        color_attribute = cls.env.ref("product.product_attribute_2")
        color_att_value_white = cls.env.ref("product.product_attribute_value_3")
        color_att_value_black = cls.env.ref("product.product_attribute_value_4")
        legs_attribute = cls.env.ref("product.product_attribute_1")
        legs_att_value_steel = cls.env.ref("product.product_attribute_value_1")
        legs_att_value_alu = cls.env.ref("product.product_attribute_value_2")
        cls._add_variants(
            product_template,
            {
                color_attribute: [color_att_value_white, color_att_value_black],
                legs_attribute: [legs_att_value_steel, legs_att_value_alu],
            },
        )

    @classmethod
    def _add_variants(cls, product_template, attribute_values_dict):
        for attribute, att_values_list in attribute_values_dict.items():
            cls.env["product.template.attribute.line"].create(
                {
                    "product_tmpl_id": product_template.id,
                    "attribute_id": attribute.id,
                    "value_ids": [
                        fields.Command.set([att_val.id for att_val in att_values_list])
                    ],
                }
            )

    @classmethod
    def _create_bom_with_variants(cls):
        attribute_values_dict = {
            att_val.product_attribute_value_id.name: att_val.id
            for att_val in cls.env["product.template.attribute.value"].search(
                [("product_tmpl_id", "=", cls.bom_product_template.id)]
            )
        }
        new_bom_form = Form(cls.env["mrp.bom"])
        new_bom_form.product_tmpl_id = cls.bom_product_template
        new_bom = new_bom_form.save()
        bom_line_create_values = []
        for product in cls.product_template_tracked_by_sn.product_variant_ids:
            create_values = {"bom_id": new_bom.id}
            create_values["product_id"] = product.id
            att_values_commands = []
            for att_value in product.product_template_attribute_value_ids:
                att_values_commands.append(
                    fields.Command.link(attribute_values_dict[att_value.name])
                )
            create_values[
                "bom_product_template_attribute_value_ids"
            ] = att_values_commands
            bom_line_create_values.append(create_values)
        cls.env["mrp.bom.line"].create(bom_line_create_values)
        new_bom_form = Form(new_bom)
        new_bom_form.lot_number_propagation = True
        for line_position, _bom_line in enumerate(new_bom.bom_line_ids):
            new_bom_line_form = new_bom_form.bom_line_ids.edit(line_position)
            new_bom_line_form.propagate_lot_number = True
            new_bom_line_form.save()
        return new_bom_form.save()
