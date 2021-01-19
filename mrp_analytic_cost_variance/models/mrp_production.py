# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _prepare_estimate_line(self, material=None, operation=None):
        self.ensure_one()
        assert not (material and operation)
        if operation:
            return {
                "production_id": self.id,
                # TODO: consider removing the analytic_activity_cost dependency
                "product_id": operation.workcenter_id.analytic_product_id.id,
                "unit_cost": operation.workcenter_id.costs_hour,
                "quantity_estimate": operation.duration_expected / 60,
                "work_order_id": operation.id,
            }
        if material:
            return {
                "production_id": self.id,
                "product_id": material.product_id.id,
                "unit_cost": material.product_id.standard_price,
                "quantity_estimate": material.product_uom_qty,
                "stock_move_id": material.id,
            }

    def create_analytic_estimate(self):
        MrpEstimate = self.env["mrp.analytic.estimate"].sudo()
        for mo in self:
            if not mo.analytic_account_id:
                raise exceptions.UserError(
                    _(
                        "An Analytic Account is required. "
                        "Please set it on on Manufacturing Order %s"
                    )
                    % mo.name,
                )
            for operation in mo.workorder_ids:
                vals = mo._prepare_estimate_line(operation=operation)
                MrpEstimate.create(vals)
            for material in mo.move_raw_ids:
                vals = mo._prepare_estimate_line(material=material)
                MrpEstimate.create(vals)

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        self.create_analytic_estimate()
        return res

    # FIXME: non planned items are not shown in the sumamry view ...
    # Create a Report SQL view for this?
