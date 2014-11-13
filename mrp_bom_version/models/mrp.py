# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _track = {
        'state': {
            'mrp_bom_version.mt_active': lambda self, cr, uid, obj,
            ctx=None: obj.state == 'active',
        },
    }

    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'Active'),
                              ('historical', 'Historical'),
                              ], string='Status', index=True, readonly=True,
                             default='draft', copy=False)

    @api.one
    @api.constrains('sequence')
    def check_mrp_bom_sequence(self):
        domain = [('id', '!=', self.id), ('sequence', '=', self.sequence)]
        if self.product_tmpl_id:
            domain.append(('product_tmpl_id', '=', self.product_tmpl_id.id))
        else:
            domain.append(('product_tmpl_id', '=', False))
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        else:
            domain.append(('product_id', '=', False))
        found = self.search(domain)
        if found:
            raise exceptions.Warning(
                _('The sequence must be unique'))

    @api.one
    def copy(self, default=None):
        bom = self.search([], order='sequence desc', limit=1)
        maxseq = bom.sequence + 1
        default.update({'sequence': maxseq})
        return super(MrpBom, self).copy(default=default)

    @api.multi
    def button_active(self):
        return self.write({'state': 'active'})

    @api.multi
    def button_historical(self):
        return self.write({'state': 'historical',
                           'historical_date': fields.Date.today()})


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def product_id_change(self, cr, uid, ids, product_id, product_qty=0,
                          context=None):
        bom_obj = self.pool['mrp.bom']
        product_obj = self.pool['product.product']
        res = super(MrpProduction, self).product_id_change(
            cr, uid, ids, product_id=product_id, product_qty=product_qty,
            context=context)
        if product_id:
            res['value'].update({'bom_id': False})
            product_tmpl_id = product_obj.browse(
                cr, uid, product_id, context=context).product_tmpl_id.id
            domain = [('state', '=', 'active'),
                      '|',
                      ('product_id', '=', product_id),
                      '&',
                      ('product_id', '=', False),
                      ('product_tmpl_id', '=', product_tmpl_id)
                      ]
            domain = domain + ['|', ('date_start', '=', False),
                               ('date_start', '<=', fields.Datetime.now()),
                               '|', ('date_stop', '=', False),
                               ('date_stop', '>=', fields.Datetime.now())]
            bom_ids = bom_obj.search(cr, uid, domain, context=context)
            bom_id = 0
            min_seq = 0
            for bom in bom_obj.browse(cr, uid, bom_ids, context=context):
                if min_seq == 0 or bom.sequence < min_seq:
                    min_seq = bom.sequence
                    bom_id = bom.id
            if bom_id > 0:
                res['value'].update({'bom_id': bom_id})
        return res
