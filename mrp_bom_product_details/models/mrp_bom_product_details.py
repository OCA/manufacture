# -*- coding: utf-8 -*-
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    product_standard_price = fields.Float(
        related='product_id.standard_price', string='Cost Price',
        readonly=True)

    product_qty_available = fields.Float(
        related='product_id.qty_available',
        string='Quantity On Hand', readonly=True)


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_standard_price = fields.Float(related='product_id.standard_price',
                                          readonly=True)
    product_qty_available = fields.Float(related='product_id.qty_available',
                                         readonly=True)
