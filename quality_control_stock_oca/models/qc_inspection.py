# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_picking", store=True
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot", compute="_compute_lot", store=True
    )

    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend(
            [
                ("stock.picking", "Picking List"),
                ("stock.move", "Stock Move"),
                ("stock.lot", "Lot/Serial Number"),
            ]
        )
        return result

    @api.depends("object_id")
    def _compute_picking(self):
        for inspection in self.filtered("object_id"):
            if inspection.object_id._name == "stock.move":
                inspection.picking_id = inspection.object_id.picking_id
            elif inspection.object_id._name == "stock.picking":
                inspection.picking_id = inspection.object_id

    @api.depends("object_id")
    def _compute_lot(self):
        moves = self.filtered(
            lambda i: i.object_id and i.object_id._name == "stock.move"
        ).mapped("object_id")
        move_lines = self.env["stock.move.line"].search(
            [("lot_id", "!=", False), ("move_id", "in", [move.id for move in moves])]
        )
        for inspection in self.filtered("object_id"):
            if inspection.object_id._name == "stock.move":
                inspection.lot_id = first(
                    move_lines.filtered(lambda x: x.move_id == inspection.object_id)
                ).lot_id
            elif inspection.object_id._name == "stock.lot":
                inspection.lot_id = inspection.object_id

    @api.depends("object_id")
    def _compute_product_id(self):
        """Overriden for getting the product from a stock move."""
        res = super()._compute_product_id()
        for inspection in self.filtered("object_id"):
            if inspection.object_id._name == "stock.move":
                inspection.product_id = inspection.object_id.product_id
            elif inspection.object_id._name == "stock.lot":
                inspection.product_id = inspection.object_id.product_id
        return res

    @api.onchange("object_id")
    def onchange_object_id(self):
        if self.object_id and self.object_id._name == "stock.move":
            self.qty = self.object_id.product_qty

    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super()._prepare_inspection_header(object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == "stock.move":
            res["qty"] = object_ref.product_uom_qty
        return res


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking_id", store=True
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot", related="inspection_id.lot_id", store=True
    )
