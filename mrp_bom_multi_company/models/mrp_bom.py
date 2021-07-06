# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    company_id = fields.Many2one(
        default=lambda self: self.env['res.company']._company_default_get('mrp.bom'),
        required=False
    )
