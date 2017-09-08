# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _sql_constraint = (
        'uniq_product_template',
        'uniq(product_tmpl_id)',
        _('You can only have one Bom per product template'),
        )


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        related='bom_id.product_tmpl_id',
        readonly=True,
        store=True)
