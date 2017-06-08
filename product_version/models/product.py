# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.tools import config


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    _track = {
        'state': {
            'product_version.mt_active': lambda self, cr, uid, obj,
            ctx=None: obj.state == 'sellable',
        },
    }

    @api.one
    def _get_old_versions(self):
        parent = self.parent_product
        old_version = self.env['product.template']
        while parent:
            old_version += parent
            parent = parent.parent_product
        self.old_versions = old_version

    active = fields.Boolean(
        default=False,
        readonly=True, states={'draft': [('readonly', False)]})
    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('sellable', 'Active'), ('end', 'End'),
                   ('obsolete', 'Historical')], string='State',
        index=True, readonly=True, default='draft', copy=False)
    name = fields.Char(
        states={'obsolete': [('readonly', True)]})
    code = fields.Char(
        states={'obsolete': [('readonly', True)]})

    # type = fields.Selection(
    #    states={'obsolete': [('readonly', True)]})
    # company_id = fields.Many2one(
    #     states={'obsolete': [('readonly', True)]})
    # product_uom = fields.Many2one(
    #     states={'obsolete': [('readonly', True)]})
    # position = fields.Char(
    #     states={'obsolete': [('readonly', True)]})
    # date_start = fields.Date(
    #     states={'obsolete': [('readonly', True)]})
    # date_stop = fields.Date(
    #     states={'obsolete': [('readonly', True)]})
    # property_ids = fields.Many2many(
    #     states={'obsolete': [('readonly', True)]})
    # message_follower_ids = fields.Many2many(
    #     states={'obsolete': [('readonly', True)]})
    # message_ids = fields.One2many(
    #     states={'obsolete': [('readonly', True)]})

    version = fields.Integer(states={'obsolete': [('readonly', True)]},
                             copy=False, default=1)
    parent_product = fields.Many2one(
        comodel_name='product.template', string='Parent Product')
    old_versions = fields.Many2many(
        comodel_name='product.template', string='Old Versions',
        compute='_get_old_versions')

    @api.multi
    def button_draft(self):
        active_product_draft = self.env['mrp.config.settings']._get_parameter(
            'active.product.draft')
        self.write({
            'active': active_product_draft and active_product_draft.value or
            False,
            'state': 'draft',
        })

    @api.multi
    def button_new_version(self):
        self.ensure_one()
        new_product = self._copy_product()
        self.button_historical()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form, tree',
            'view_mode': 'form',
            'res_model': 'product.template',
            'res_id': new_product.id,
            'target': 'current',
        }

    def _copy_product(self):
        active_product_draft = self.env['mrp.config.settings']._get_parameter(
            'active.product.draft')
        new_product = self.copy({
            'version': self.version + 1,
            'active': active_product_draft and active_product_draft.value or
            False,
            'parent_product': self.id,
        })
        return new_product

    @api.multi
    def button_activate(self):
        self.write({
            'active': True,
            'state': 'sellable'
        })

    @api.multi
    def button_historical(self):
        self.write({
            'active': False,
            'state': 'obsolete',
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
        return super(ProductTemplate, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)

    @api.model
    def _product_find(
            self, product_tmpl_id=None, product_id=None, properties=None):
        """ Finds BoM for particular product and product uom.
        @param product_tmpl_id: Selected product.
        @param product_uom: Unit of measure of a product.
        @param properties: List of related properties.
        @return: False or BoM id.
        """
        product_id = super(
            ProductTemplate, self.with_context(state='sellable')).\
            _product_find(
            product_tmpl_id=product_tmpl_id, product_id=product_id,
            properties=properties)
        return product_id
