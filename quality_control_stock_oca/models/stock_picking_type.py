# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def _create_qc_trigger(self):
        langs = self.env['ir.translation'].search([('name', '=', 'stock.picking.type,name'),
                                                   ('res_id', 'in', self.ids),
                                                   ('lang', '!=', 'en_US')])
        for picking_type in self:
            type_lang = langs.filtered(lambda x: x.res_id == picking_type.id)
            qc_trigger = {
                "name": picking_type.name,
                "company_id": picking_type.warehouse_id.company_id.id,
                "picking_type_id": picking_type.id,
                "partner_selectable": True,
            }
            trig = self.env["qc.trigger"].sudo().create(qc_trigger)
            for lang in type_lang:
                qc_trigger_tran = {'name': 'qc.trigger,name',
                                   'res_id': trig.id,
                                   'lang': lang.lang,
                                   'type': 'model',
                                   'src': picking_type.name,
                                   'value': lang.value,
                                   'state': 'translated',
                                   'module': 'quality_control_oca'}
                self.env['ir.translation'].sudo().create(qc_trigger_tran)

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
