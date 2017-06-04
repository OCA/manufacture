# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    product_standard_price = fields.Float(related='product_id.standard_price',
                                          string='Cost Price', readonly=True)
    product_qty_available = fields.Float(related='product_id.qty_available',
                                         string='Quantity On Hand',
                                         readonly=True)


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_standard_price = fields.Float(related='product_id.standard_price',
                                          string='Cost Price', readonly=True)
    product_qty_available = fields.Float(related='product_id.qty_available',
                                         string='Quantity On Hand',
                                         readonly=True)
