# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

WORKORDER_FIELDS = {
    "workorder_ids",
    "bom_id",
    "product_id",
    "product_qty",
    "product_uom_id",
    "never_product_template_attribute_value_ids",
}


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _reset_work_order_sequence(self):
        for production in self:
            workorders = production.workorder_ids.sorted(
                lambda wo: (not wo._origin, wo.sequence, wo._origin.id)
            )
            for sequence, workorder in enumerate(workorders, 1):
                if workorder.sequence != sequence:
                    workorder.sequence = sequence

    @api.depends(
        "bom_id",
        "product_id",
        "product_qty",
        "product_uom_id",
        "never_product_template_attribute_value_ids",
    )
    def _compute_workorder_ids(self):
        res = super()._compute_workorder_ids()
        self.filtered(
            lambda p: not p.id and p.state == "draft"
        )._reset_work_order_sequence()
        return res

    def write(self, vals):
        if WORKORDER_FIELDS.isdisjoint(vals) or self.env.context.get(
            "_skip_reset_work_order_sequence"
        ):
            return super().write(vals)
        res = super(
            MrpProduction, self.with_context(_skip_reset_work_order_sequence=True)
        ).write(vals)
        self._reset_work_order_sequence()
        return res
