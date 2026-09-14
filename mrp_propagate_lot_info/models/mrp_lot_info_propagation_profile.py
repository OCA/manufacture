# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class MrpLotInfoPropagationProfile(models.Model):
    _name = "mrp.lot.info.propagation.profile"
    _description = "MRP Lot Info Propagation Profile"

    name = fields.Char(required=True, translate=True)
    propagate_lot_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Lot fields to propagate",
        domain=[
            ("model", "=", "stock.lot"),
            ("readonly", "=", False),
            ("name", "not in", ["company_id", "name", "product_id"]),
            ("store", "=", True),
            ("ttype", "not in", ["binary", "many2many", "one2many"]),
        ],
        required=True,
    )
