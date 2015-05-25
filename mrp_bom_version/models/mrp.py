# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _track = {
        'state': {
            'mrp_bom_version.mt_active': lambda self, cr, uid, obj,
            ctx=None: obj.state == 'active',
        },
    }

    active = fields.Boolean(
        string='Active', default=False, readonly=True,
        states={'draft': [('readonly', False)]})
    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'Active'),
                              ('historical', 'Historical'),
                              ], string='Status', index=True, readonly=True,
                             default='draft', copy=False)
    product_tmpl_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    product_qty = fields.Float(
        readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(
        states={'historical': [('readonly', True)]})
    code = fields.Char(
        states={'historical': [('readonly', True)]})
    type = fields.Selection(
        states={'historical': [('readonly', True)]})
    company_id = fields.Many2one(
        states={'historical': [('readonly', True)]})
    product_uom = fields.Many2one(
        states={'historical': [('readonly', True)]})
    routing_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    bom_line_ids = fields.One2many(
        readonly=True, states={'draft': [('readonly', False)]})
    position = fields.Char(
        states={'historical': [('readonly', True)]})
    date_start = fields.Date(
        states={'historical': [('readonly', True)]})
    date_stop = fields.Date(
        states={'historical': [('readonly', True)]})
    property_ids = fields.Many2many(
        states={'historical': [('readonly', True)]})
    product_rounding = fields.Float(
        states={'historical': [('readonly', True)]})
    product_efficiency = fields.Float(
        states={'historical': [('readonly', True)]})
    message_follower_ids = fields.Many2many(
        states={'historical': [('readonly', True)]})
    message_ids = fields.One2many(
        states={'historical': [('readonly', True)]})
    version = fields.Integer(states={'historical': [('readonly', True)]},
                             copy=False, default=1)

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.multi
    def button_new_version(self):
        self.ensure_one()
        self.write({'active': False, 'state': 'historical',
                    'historical_date': fields.Date.today()})
        version = self.version + 1
        new_bom = self.copy({'version': version})
        new_bom.active = True
        return {'type': 'ir.actions.act_window',
                'view_type': 'form, tree',
                'view_mode': 'form',
                'res_model': 'mrp.bom',
                'res_id': new_bom.id,
                'target': 'new',
                }

    @api.one
    def button_activate(self):
        return self.write({'active': True, 'state': 'active'})

    @api.one
    def button_historical(self):
        return self.write({'active': False, 'state': 'historical',
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
