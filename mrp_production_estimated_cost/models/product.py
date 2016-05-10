# -*- coding: utf-8 -*-
# (c) 2014-2015 Avanzosc
# (c) 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manual_standard_cost = fields.Float(
        string='Manual Standard Cost', digits=dp.get_precision('Product Price')
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    manual_standard_cost = fields.Float(
        string='Manual Standard Cost', digits=dp.get_precision('Product Price')
    )

    @api.multi
    def write(self, vals):
        if 'manual_standard_cost' in vals:
            templates = self.mapped('product_tmpl_id').filtered(
                lambda x: len(x.attribute_line_ids) == 1)
            templates.write({'manual_standard_cost':
                             vals.get('manual_standard_cost')})
        return super(ProductProduct, self).write(vals)
