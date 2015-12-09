# -*- coding: utf-8 -*-
# (c) 2015 Savoir-faire Linux - <http://www.savoirfairelinux.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class MrpBillOfMaterialReference(models.Model):
    _name = 'mrp.bom.reference'
    _description = 'MRP Bill of Material Reference'

    bom_id = fields.Many2one(
        comodel_name='mrp.bom', required=True, ondelete='cascade',
        string='Bill of Material')
    name = fields.Char(related='bom_id.code', store=True)
