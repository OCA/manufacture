# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_production_request_id = fields.Many2one(
        comodel_name="mrp.production.request",
        string="Manufacturing Request", copy=False, readonly=True)

    def _generate_finished_moves(self):
        move = super(MrpProduction, self)._generate_finished_moves()
        mr_proc = self.mrp_production_request_id.procurement_id
        if mr_proc and mr_proc.move_dest_id:
            move.write({"move_dest_id": mr_proc.move_dest_id.id})
        return move
