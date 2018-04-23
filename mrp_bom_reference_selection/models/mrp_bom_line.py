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

from odoo import api, exceptions, fields, models, _


class MrpBillOfMaterialLine(models.Model):
    _inherit = 'mrp.bom.line'

    reference_id = fields.Many2one(
        comodel_name='mrp.bom.reference', string='Ref')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        related='product_id.product_tmpl_id', store=True)

    product_id = fields.Many2one(
        'product.product', required=True, string='Product')

    @api.constrains('reference_id')
    def _check_reference_id(self):
        if (self.reference_id and
                (self.reference_id.bom_id.product_tmpl_id !=
                 self.product_id.product_tmpl_id)):
            raise exceptions.Warning(
                _('Product %s from %s reference BoM must be equal to product'
                  ' %s in BoM line.' %
                  (self.reference_id.bom_id.product_tmpl_id.name,
                   self.reference_id.name,
                   self.product_id.product_tmpl_id.name)))

    @api.multi
    def onchange_product_id(self, product_id, product_qty=0):
        res = super(MrpBillOfMaterialLine, self).onchange_product_id(
            product_id, product_qty=product_qty)
        if 'value' not in res:
            res['value'] = {}
        if 'domain' not in res:
            res['domain'] = {}
        if product_id:
            product = self.env['product.product'].browse(product_id)
            refs = self.env['mrp.bom.reference'].search(
                [('bom_id.product_tmpl_id', '=', product.product_tmpl_id.id)])
            res['value']['reference_id'] = refs[:1]
            res['domain']['reference_id'] = [('id', 'in', refs.ids)]
        else:
            res['value']['reference_id'] = False
            res['domain']['reference_id'] = False
        return res

    @api.depends('product_id')
    def _compute_child_bom_lines(self):
        for record in self:
            if record.reference_id:
                record.child_line_ids = record.reference_id.bom_id.bom_line_ids
            else:
                bom_obj = self.env['mrp.bom']
                bom_id = bom_obj._bom_find(
                    product_tmpl_id=record.product_id.product_tmpl_id.id,
                    product_id=record.product_id.id)
                record.child_line_ids = [
                    (6, 0, bom_obj.browse(bom_id).bom_line_ids.ids)
                ]

    child_line_ids = fields.One2many(
        relation='mrp.bom.line', compute='_compute_child_bom_lines',
        string="BoM lines of the referred BoM",
    )
