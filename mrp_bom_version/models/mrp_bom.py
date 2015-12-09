# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.tools import config


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _track = {
        'state': {
            'mrp_bom_version.mt_active': lambda self, cr, uid, obj,
            ctx=None: obj.state == 'active',
        },
    }

    @api.one
    def _get_old_versions(self):
        parent = self.parent_bom
        old_version = self.env['mrp.bom']
        while parent:
            old_version += parent
            parent = parent.parent_bom
        self.old_versions = old_version

    def _default_active(self):
        """Needed for preserving normal flow when testing other modules."""
        res = False
        if config['test_enable']:
            res = not bool(self.env.context.get('test_mrp_bom_version'))
        return res

    def _default_state(self):
        """Needed for preserving normal flow when testing other modules."""
        res = 'draft'
        if (config['test_enable'] and
                not self.env.context.get('test_mrp_bom_version')):
            res = 'active'
        return res

    active = fields.Boolean(
        default=_default_active,
        readonly=True, states={'draft': [('readonly', False)]})
    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('active', 'Active'),
                   ('historical', 'Historical')], string='State',
        index=True, readonly=True, default=_default_state, copy=False)
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
    parent_bom = fields.Many2one(
        comodel_name='mrp.bom', string='Parent BoM')
    old_versions = fields.Many2many(
        comodel_name='mrp.bom', string='Old Versions',
        compute='_get_old_versions')

    @api.multi
    def button_draft(self):
        active_draft = self.env['mrp.config.settings']._get_parameter(
            'active.draft')
        self.write({
            'active': active_draft and active_draft.value or False,
            'state': 'draft',
        })

    @api.multi
    def button_new_version(self):
        self.ensure_one()
        new_bom = self._copy_bom()
        self.button_historical()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form, tree',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'res_id': new_bom.id,
            'target': 'current',
        }

    def _copy_bom(self):
        active_draft = self.env['mrp.config.settings']._get_parameter(
            'active.draft')
        new_bom = self.copy({
            'version': self.version + 1,
            'active': active_draft and active_draft.value or False,
            'parent_bom': self.id,
        })
        return new_bom

    @api.multi
    def button_activate(self):
        self.write({
            'active': True,
            'state': 'active'
        })

    @api.multi
    def button_historical(self):
        self.write({
            'active': False,
            'state': 'historical',
            'historical_date': fields.Date.today()
        })

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """Add search argument for field type if the context says so. This
        should be in old API because context argument is not the last one.
        """
        if context is None:
            context = {}
        search_state = context.get('state', False)
        if search_state:
            args += [('state', '=', search_state)]
        return super(MrpBom, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)

    @api.model
    def _bom_find(
            self, product_tmpl_id=None, product_id=None, properties=None):
        """ Finds BoM for particular product and product uom.
        @param product_tmpl_id: Selected product.
        @param product_uom: Unit of measure of a product.
        @param properties: List of related properties.
        @return: False or BoM id.
        """
        bom_id = super(MrpBom, self.with_context(state='active'))._bom_find(
            product_tmpl_id=product_tmpl_id, product_id=product_id,
            properties=properties)
        return bom_id
