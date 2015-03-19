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


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def _get_default_bom_id(self):
        active_id = self.env.context.get("active_id")
        if active_id:
            prod = self.env['mrp.production'].browse(active_id)
            if prod.bom_id:
                return prod.bom_id.id
        return False

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', default=_get_default_bom_id,
        readonly=True,
    )
