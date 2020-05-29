# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(StockMoveLine, self).create(vals_list)
        records.filtered(lambda ml: ml.move_id.is_subcontract).mapped(
            'move_id')._check_overprocessed_subcontract_qty()
        return records

    def write(self, values):
        # Same explanation as for stock.move.action_assign()
        subcontract_amls = self.filtered(lambda x: x.move_id.is_subcontract)
        if (self - subcontract_amls) or not subcontract_amls:
            res = super(StockMoveLine, self - subcontract_amls).write(values)
        if subcontract_amls:
            res = super(StockMoveLine, subcontract_amls.with_context(
                mrp_subcontracting_bypass_reservation=True)).write(values)
        self.filtered(lambda ml: ml.move_id.is_subcontract).mapped(
            'move_id')._check_overprocessed_subcontract_qty()
        return res

    def unlink(self):
        # Same explanation as for stock.move.action_assign()
        subcontract_amls = self.filtered(lambda x: x.move_id.is_subcontract)
        if (self - subcontract_amls) or not subcontract_amls:
            res = super(StockMoveLine, self - subcontract_amls).unlink()
        if subcontract_amls:
            res = super(StockMoveLine, subcontract_amls.with_context(
                mrp_subcontracting_bypass_reservation=True)).unlink()
        return res

    def _action_done(self):
        # Same explanation as for stock.move.action_assign()
        subcontract_amls = self.filtered(lambda x: x.move_id.is_subcontract)
        if (self - subcontract_amls) or not subcontract_amls:
            res = super(StockMoveLine, self - subcontract_amls)._action_done()
        if subcontract_amls:
            res = super(StockMoveLine, subcontract_amls.with_context(
                mrp_subcontracting_bypass_reservation=True))._action_done()
        return res
