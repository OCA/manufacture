# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcTestTemplateCategory(models.Model):
    _name = 'qc.test.category'
    _description = 'Test category'

    @api.one
    @api.depends('name', 'parent_id')
    def _get_complete_name(self):
        names = [self.name]
        parent = self.parent_id
        while parent:
            names.append(parent.name)
            parent = parent.parent_id
        self.complete_name = " / ".join(reversed(names))

    @api.constrains('parent_id')
    def _check_recursion(self):
        ids = self.ids
        level = 100
        while ids:
            parents = self.search([('id', 'in', ids),
                                   ('parent_id', '!=', False)])
            ids = list(set([x.parent_id.id for x in parents]))
            if not level:
                raise exceptions.Warning(
                    _('Error ! You can not create recursive categories.'))
            level -= 1

    name = fields.Char('Name', required=True, translate=True)
    parent_id = fields.Many2one(
        comodel_name='qc.test.category', string='Parent category', select=True)
    complete_name = fields.Char(
        compute="_get_complete_name", string='Full name')
    child_ids = fields.One2many(
        comodel_name='qc.test.category', inverse_name='parent_id',
        string='Child categories')
    active = fields.Boolean(
        string='Active', default=True,
        help="This field allows you to hide the category without removing it.")
