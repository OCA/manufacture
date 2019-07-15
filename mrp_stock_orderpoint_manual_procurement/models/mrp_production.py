# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    requested_by = fields.Many2one(
        comodel_name='res.users',
        track_visibility='always',
    )
