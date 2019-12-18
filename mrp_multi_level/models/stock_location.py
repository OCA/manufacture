# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    mrp_area_id = fields.Many2one(
        comodel_name="mrp.area",
        string="MRP Area",
        help="Requirements for a particular MRP area are combined for the "
        "purposes of procurement by the MRP.",
    )
