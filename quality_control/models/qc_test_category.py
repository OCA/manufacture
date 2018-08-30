# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class QcTestTemplateCategory(models.Model):
    _name = 'qc.test.category'
    _description = 'Test category'

    @api.multi
    @api.depends('name', 'parent_id')
    def _compute_get_complete_name(self):
        for record in self:
            names = [record.name or '']
            parent = record.parent_id
            while parent:
                names.append(parent.name)
                parent = parent.parent_id
            record.complete_name = " / ".join(reversed(names))

    @api.constrains('parent_id')
    def _check_recursion(self):
        ids = self.ids
        level = 100
        while ids:
            parents = self.search([('id', 'in', ids),
                                   ('parent_id', '!=', False)])
            ids = list(set([x.parent_id.id for x in parents]))
            if not level:
                raise exceptions.UserError(
                    _('Error! You can not create recursive categories.'))
            level -= 1

    name = fields.Char('Name', required=True, translate=True)
    parent_id = fields.Many2one(
        comodel_name='qc.test.category', string='Parent category')
    complete_name = fields.Char(
        compute="_compute_get_complete_name", string='Full name')
    child_ids = fields.One2many(
        comodel_name='qc.test.category', inverse_name='parent_id',
        string='Child categories')
    active = fields.Boolean(
        string='Active', default=True,
        help="This field allows you to hide the category without removing it.")
