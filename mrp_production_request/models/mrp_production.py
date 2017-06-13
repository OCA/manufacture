# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_production_request_id = fields.Many2one(
        comodel_name="mrp.production.request",
        string="Manufacturing Request", copy=False, readonly=True)
