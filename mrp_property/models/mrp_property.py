# coding: utf-8
# Copyright 2008 - 2016 Odoo S.A.
# Copyright 2018 Opener B.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpProperty(models.Model):
    """ Property to control BOM selection from the sale order """
    _name = 'mrp.property'
    _description = 'MRP Property'

    name = fields.Char(required=True)
    group_id = fields.Many2one(
        'mrp.property.group', 'Property Group', required=True)
    description = fields.Text()

    @api.multi
    def unlink(self):
        """ Restrict the removal of properties that are in use """
        if self.env['sale.order.line'].sudo().search(
                [('property_ids', 'in', self.ids)]):
            raise UserError('You cannot delete this property, because it has '
                            'been assigned to a sale order line.')
        return super(MrpProperty, self).unlink()
