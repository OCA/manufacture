from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "move_raw_ids.state",
        "move_raw_ids.quantity_done",
        "move_finished_ids.state",
        "workorder_ids",
        "workorder_ids.state",
        "product_qty",
        "qty_producing",
    )
    def _compute_state(self):
        super(MrpProduction, self)._compute_state()
        for prod in self.filtered(lambda prod: prod.state == "done"):
            pickings = prod.move_finished_ids.mapped(
                "move_dest_ids.picking_id"
            ).filtered(lambda p: p.state == "subcontracted")
            if not pickings:
                continue
            for picking in pickings:
                # Picking set state 'Ready'
                picking.action_confirm()
                picking.action_assign()
