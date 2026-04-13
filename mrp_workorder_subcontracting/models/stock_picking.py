from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sub_workorder_count = fields.Integer(
        string="Number of Subcontract Workorders",
        compute="_compute_sub_workorder_count",
    )

    @api.depends(
        "picking_type_code",
        "move_ids.sub_delivery_workorder_id",
        "move_ids.sub_return_workorder_id",
    )
    def _compute_sub_workorder_count(self):
        for picking in self:
            if picking.picking_type_code == "incoming":
                workorders = picking.move_ids.mapped("sub_return_workorder_id")
            elif picking.picking_type_code == "outgoing":
                workorders = picking.move_ids.mapped("sub_delivery_workorder_id")
            else:
                workorders = self.env["mrp.workorder"]

            picking.sub_workorder_count = len(workorders)
