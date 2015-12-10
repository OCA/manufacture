# -*- coding: utf-8 -*-
# (c) 2015 Savoir-faire Linux - <http://www.savoirfairelinux.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpBillOfMaterial(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def create(self, vals):
        res = super(MrpBillOfMaterial, self).create(vals)
        if not res.reference_id:
            self.env['mrp.bom.reference'].create({'bom_id': res.id})
        return res

    reference_id = fields.One2many(
        comodel_name='mrp.bom.reference', inverse_name='bom_id',
        string="BoM Reference")
