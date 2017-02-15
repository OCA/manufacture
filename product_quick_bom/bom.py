# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from collections import defaultdict
from odoo.exceptions import Warning as UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _sql_constraint = (
        'uniq_product_template',
        'uniq(product_tmpl_id)',
        'You can only have one Bom per product template',
        )


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_tmpl_id = fields.Many2one(
        'product.template',
        related='bom_id.product_tmpl_id',
        store=True)
