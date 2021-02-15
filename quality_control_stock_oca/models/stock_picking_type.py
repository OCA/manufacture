# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def _create_qc_trigger(self):
        for picking_type in self:
            qc_trigger = {
                "name": picking_type.name,
                "company_id": picking_type.warehouse_id.company_id.id,
                "picking_type_id": picking_type.id,
                "partner_selectable": True,
            }
            self.env["qc.trigger"].sudo().create(qc_trigger)

    @api.model_create_multi
    def create(self, val_list):
        picking_types = super().create(val_list)
        picking_types._create_qc_trigger()
        return picking_types

    def write(self, vals):
        res = super().write(vals)
        if vals.get("name") or vals.get("warehouse_id"):
            qc_trigger_model = self.env["qc.trigger"].sudo()
            for rec in self:
                qc_triggers = qc_trigger_model.search(
                    [("picking_type_id", "=", rec.id)]
                )
                qc_triggers.write({"name": rec.name})
        return res
