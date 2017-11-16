# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class MrpBillOfMaterialLine(models.Model):
    _inherit = 'mrp.bom.line'

    reference_id = fields.Many2one('mrp.bom.reference', 'Ref')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        related='product_id.product_tmpl_id', store=True)

    product_id = fields.Many2one(
        'product.product', required=True, string='Product')

    @api.multi
    def onchange_product_id(self, product_id):
        product = self.env['product.product'].browse(product_id)

        res = {'value': {}}

        if not product:
            res['value']['reference_id'] = False
        else:
            refs = self.env['mrp.bom.reference'].search(
                [('bom_id.product_tmpl_id', '=', product.product_tmpl_id.id)])
            res['value']['reference_id'] = refs and refs[0]

        return res

    @api.one
    @api.depends('product_id')
    def _get_child_bom_lines(self):
        if self.reference_id:
            self.child_line_ids = self.reference_id.bom_id.bom_line_ids.ids
        else:
            bom_obj = self.env['mrp.bom']
            bom_id = bom_obj._bom_find(
                product_tmpl_id=self.product_id.product_tmpl_id.id,
                product_id=self.product_id.id)
            self.child_line_ids = bom_id and [
                (6, 0, child_id) for child_id in
                bom_obj.browse(bom_id).bom_line_ids.ids
            ] or False

    child_line_ids = fields.One2many(
        relation='mrp.bom.line',
        compute='_get_child_bom_lines',
        string="BOM lines of the referred bom",
    )
