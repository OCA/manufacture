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


class MrpBillOfMaterial(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def create(self, vals):
        res = super(MrpBillOfMaterial, self).create(vals)
        if not res.reference_id:
            self.env['mrp.bom.reference'].create({'bom_id': res.id})
        return res

    reference_id = fields.One2many(
        'mrp.bom.reference', 'bom_id', string="BoM Reference")
