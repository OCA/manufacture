# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location",
        help="Set the preferred location for this BOM.",
        domain=[('usage', '=', 'internal')])


class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location",
        help="Location which it is expected to get the products from.",
        domain=[('usage', '=', 'internal')])
