# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_lot_id_editable = fields.Boolean(
        string="Is lot editable?",
        compute="_compute_is_lot_id_editable",
        help="Technical field to define if the 'lot_id' field is editable.",
    )

    @api.depends("lot_id")
    def _compute_is_lot_id_editable(self):
        for line in self:
            line.is_lot_id_editable = True
            mos = line.move_id.move_orig_ids.production_id
            lot_prapagated = [
                mo.propagated_lot_producing == line.lot_id.name
                and mo.subcontracting_has_been_recorded
                and mo.is_lot_number_propagated
                for mo in mos
            ]
            if any(lot_prapagated):
                line.is_lot_id_editable = False
