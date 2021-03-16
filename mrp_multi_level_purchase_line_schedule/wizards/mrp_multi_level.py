# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import date

from odoo import api, fields, models


class MultiLevelMrp(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    def _prepare_mrp_move_data_from_po_line_schedule(self, sl, product_mrp_area):
        mrp_date = date.today()
        if fields.Date.from_string(sl.date_planned) > date.today():
            mrp_date = fields.Date.from_string(sl.date_planned)
        return {
            "product_id": sl.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": None,
            "purchase_order_id": sl.order_id.id,
            "purchase_line_id": sl.order_line_id.id,
            "stock_move_id": None,
            "mrp_qty": sl.product_qty,
            "current_qty": sl.product_qty,
            "mrp_date": mrp_date,
            "current_date": sl.date_planned,
            "mrp_type": "s",
            "mrp_origin": "po",
            "mrp_order_number": sl.order_id.name,
            "parent_product_id": None,
            "name": sl.order_id.name,
            "state": sl.order_id.state,
        }

    @api.model
    def _create_mrp_move_from_purchase_order(self, line, product_mrp_area):
        if line.schedule_line_ids:
            for sl in line.schedule_line_ids:
                mrp_move_data = self._prepare_mrp_move_data_from_po_line_schedule(
                    sl, product_mrp_area
                )
                self.env["mrp.move"].create(mrp_move_data)
        else:
            return super(MultiLevelMrp, self)._create_mrp_move_from_purchase_order(
                line, product_mrp_area
            )
