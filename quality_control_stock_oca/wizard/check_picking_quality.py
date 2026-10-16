from odoo import fields, models


class QcCheckPicking(models.TransientModel):
    _name = "quality_control_stock_oca.check.picking"
    _description = "Check Quality Control of Pickings"

    stock_picking_ids = fields.Many2many(comodel_name="stock.picking")

    def action_skip_inspections(self):
        return self.stock_picking_ids.with_context(
            qc_stock_oca_skip_inspections=True
        ).button_validate()

    def action_complete_inspections(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "quality_control_stock_oca.action_qc_inspection_per_picking"
        )
        action["domain"] = [("picking_id", "in", self.stock_picking_ids.ids)]
        return action
