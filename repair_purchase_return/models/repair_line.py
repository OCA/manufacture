# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class RepairLine(models.Model):
    _inherit = "repair.line"

    purchase_return_line_ids = fields.Many2many(
        comodel_name="purchase.return.order.line", copy=False
    )

    @api.model
    def _get_purchase_return_line_onchange_product_fields(self):
        return ["price_unit", "taxes_id", "refund_only"]

    @api.model
    def _execute_purchase_return_line_onchange(self, vals):
        cls = self.env["purchase.return.order.line"]
        onchanges_dict = {
            "onchange_product_id": self._get_purchase_return_line_onchange_product_fields()
        }
        for onchange_method, changed_fields in onchanges_dict.items():
            if any(f not in vals for f in changed_fields):
                obj = cls.new(vals)
                getattr(obj, onchange_method)()
                for field in changed_fields:
                    vals[field] = obj._fields[field].convert_to_write(obj[field], obj)

    @api.model
    def _prepare_purchase_order_line_vals(self, pro):
        vals = {
            "name": self.name,
            "order_id": pro.id,
            "product_id": self.product_id.id,
            "product_uom": self.product_uom.id,
            "price_unit": 0.0,
            "product_qty": self.product_uom_qty,
            "repair_line_ids": [(4, self.id)],
            "date_planned": fields.Datetime.now(),
            "refund_only": True,
            "display_type": "product",
        }
        self._execute_purchase_return_line_onchange(vals)
        return vals
