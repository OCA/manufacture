# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import random
import string

from odoo import fields
from odoo.tests import Form, common


class Common(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._create_product_attributes()
        cls._create_products()
        cls._create_bom()
        cls._create_existing_lot()
        cls.line_tracked_by_lot = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id == cls.product_tracked_by_lot
        )
        cls.line_tracked_by_sn = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id == cls.product_tracked_by_sn
        )
        cls.line_no_tracking = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id.tracking == "none"
        )[:1]

    @classmethod
    def _create_product_attributes(cls):
        """Create the 'Trucks' attribute used by the variant tests."""
        cls.trucks_attribute = cls.env["product.attribute"].create(
            {"name": "Trucks", "display_type": "radio"}
        )
        cls.trucks_att_value_steel = cls.env["product.attribute.value"].create(
            {"name": "Steel", "attribute_id": cls.trucks_attribute.id}
        )
        cls.trucks_att_value_alu = cls.env["product.attribute.value"].create(
            {"name": "Aluminium", "attribute_id": cls.trucks_attribute.id}
        )

    @classmethod
    def _create_products(cls):
        """Create a skateboard and its components."""
        # Finished product of the BOM, tracked by serial.
        cls.bom_product_template = cls.env["product.template"].create(
            {
                "name": "Skateboard",
                "tracking": "serial",
                "is_storable": True,
                "type": "consu",  # never consumed alone: it is manufactured
            }
        )
        cls.bom_product_product = cls.bom_product_template.product_variant_ids[0]
        # Component tracked by serial, whose serial is propagated.
        cls.product_tracked_by_sn = cls.env["product.product"].create(
            {
                "name": "Deck",
                "tracking": "serial",
                "is_storable": True,
                "standard_price": 50,
            }
        )
        cls.product_template_tracked_by_sn = cls.product_tracked_by_sn.product_tmpl_id
        # Component tracked by lot.
        cls.product_tracked_by_lot = cls.env["product.product"].create(
            {
                "name": "Trucks",
                "tracking": "lot",
                "is_storable": True,
                "standard_price": 20,
            }
        )
        # Component without any tracking.
        cls.product_no_tracking = cls.env["product.product"].create(
            {"name": "Wheels", "is_storable": True, "standard_price": 5}
        )

    @classmethod
    def _create_bom(cls):
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.bom_product_template.id,
                "product_qty": 1.0,
                "consumption": "flexible",
            }
        )
        cls.env["mrp.bom.line"].create(
            [
                {
                    "bom_id": cls.bom.id,
                    "product_id": cls.product_tracked_by_sn.id,
                    "product_qty": 1,
                    "sequence": 1,
                },
                {
                    "bom_id": cls.bom.id,
                    "product_id": cls.product_tracked_by_lot.id,
                    "product_qty": 2,
                    "sequence": 2,
                },
                {
                    "bom_id": cls.bom.id,
                    "product_id": cls.product_no_tracking.id,
                    "product_qty": 4,
                    "sequence": 3,
                },
            ]
        )

    @classmethod
    def _create_existing_lot(cls):
        """A pre-existing serial number for the serial-tracked component."""
        cls.existing_lot = cls.env["stock.lot"].create(
            {
                "name": "DK001",
                "product_id": cls.product_tracked_by_sn.id,
            }
        )
        cls.LOT_NAME = cls.existing_lot.name

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
            quantity=quantity,
            package_id=package,
            lot_id=lot,
            in_date=in_date,
        )

    @classmethod
    def _update_stock_component_qty(cls, order=None, bom=None, location=None):
        """Add enough stock for all the BOM components.

        Serial-tracked products must get one lot per unit of stock, as they
        can only hold 1 unit per lot. The first serial of the propagating
        component (the deck) is the pre-existing lot (DK001), which the tests
        expect to be propagated.
        """
        if not order and not bom:
            return
        if order:
            bom = order.bom_id
        if not location:
            location = cls.env.ref("stock.stock_location_stock")
        for line in bom.bom_line_ids:
            product = line.product_id
            if not product.is_storable:
                continue
            quantity = line.product_qty
            if order:
                quantity *= order.product_qty
            if product.tracking == "serial":
                # one lot per unit for serial-tracked products
                for i in range(int(quantity)):
                    if product == cls.product_tracked_by_sn and i == 0:
                        lot = cls.existing_lot
                    else:
                        lot = cls.env["stock.lot"].create(
                            {
                                "product_id": product.id,
                                "company_id": product.company_id.id,
                                "name": f"{cls.LOT_NAME[:-3]}{i + 1:03d}",
                            }
                        )
                    cls._update_qty_in_location(location, product, 1, lot=lot)
            elif product.tracking == "lot":
                lot_name = "".join(
                    random.choice(string.ascii_lowercase) for i in range(10)
                )
                lot = cls.env["stock.lot"].create(
                    {
                        "product_id": product.id,
                        "company_id": product.company_id.id,
                        "name": lot_name,
                    }
                )
                cls._update_qty_in_location(location, product, quantity, lot=lot)
            else:
                cls._update_qty_in_location(location, product, quantity)

    @classmethod
    def _add_trucks_variants(cls, product_template):
        cls._add_variants(
            product_template,
            {
                cls.trucks_attribute: [
                    cls.trucks_att_value_steel,
                    cls.trucks_att_value_alu,
                ],
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
            create_values["bom_product_template_attribute_value_ids"] = (
                att_values_commands
            )
            bom_line_create_values.append(create_values)
        cls.env["mrp.bom.line"].create(bom_line_create_values)
        new_bom_form = Form(new_bom)
        new_bom_form.lot_number_propagation = True
        for line_position, _bom_line in enumerate(new_bom.bom_line_ids):
            new_bom_line_form = new_bom_form.bom_line_ids.edit(line_position)
            new_bom_line_form.propagate_lot_number = True
            new_bom_line_form.save()
        return new_bom_form.save()
