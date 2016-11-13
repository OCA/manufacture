# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    raw_material_procurement_group_id = fields.Many2one(
        string="Raw Material Procurement Group",
        comodel_name="procurement.group",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            },
    )
    auto_create_procurement_group = fields.Boolean(
        string="Auto Create Procurement Group",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            },
        )

    @api.multi
    def action_confirm(self):
        for mo in self:
            mo._create_procurement_group()
        return super(MrpProduction, self).action_confirm()

    @api.multi
    def _create_procurement_group(self):
        self.ensure_one()
        obj_group = self.env[
            "procurement.group"]
        if self.auto_create_procurement_group and \
                not self.raw_material_procurement_group_id:
            obj_group.create({
                "name": self.name,
                })

    @api.model
    def _make_consume_line_from_data(
            self,
            production, product, uom_id, qty,
            uos_id, uos_qty):

        move_id = super(MrpProduction, self)._make_consume_line_from_data(
            production, product, uom_id, qty,
            uos_id, uos_qty)
        obj_move = self.env["stock.move"]
        move = obj_move.browse(move_id)
        if move.procure_method == "make_to_stock":
            return move_id
        if not production.raw_material_procurement_group_id:
            return move_id
        move.write(
            {"group_id": production.raw_material_procurement_group_id.id})
        return move_id
