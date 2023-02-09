# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import random
import string

from odoo.tests import common


class Common(common.SavepointCase):

    PACKAGE_NAME = "PROPAGATED-PKG"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_desk")

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
            lot = package = None
            if line.product_id.tracking != "none":
                lot_name = "".join(
                    random.choice(string.ascii_lowercase) for i in range(10)
                )
                vals = {
                    "product_id": line.product_id.id,
                    "company_id": line.company_id.id,
                    "name": lot_name,
                }
                lot = cls.env["stock.production.lot"].create(vals)
            if line.propagate_package:
                vals = {"name": cls.PACKAGE_NAME}
                package = cls.env["stock.quant.package"].create(vals)
            cls._update_qty_in_location(
                location,
                line.product_id,
                line.product_qty,
                package=package,
                lot=lot,
            )
