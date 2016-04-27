# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bom_count = fields.Integer(compute='_bom_count',
                               string='# Bill of Material')

    @api.multi
    def _bom_count(self):
        """ Override parent method to filter out dismantling bom.
        """
        for template in self:
            template.bom_count = self.env['mrp.bom'].search_count([
                ('product_tmpl_id', '=', template.id),
                ('dismantling', '=', False),
            ])
