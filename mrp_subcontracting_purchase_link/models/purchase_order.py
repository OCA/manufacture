# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    subcontract_production_count = fields.Integer(
        compute="_compute_subcontract_production_count"
    )

    subcontract_production_ids = fields.One2many(
        "mrp.production",
        "purchase_order_id",
        "Subcontract Production Orders",
        readonly=True,
    )

    subcontract_picking_count = fields.Integer(
        compute="_compute_subcontract_picking_ids"
    )

    subcontract_picking_ids = fields.Many2many(
        compute="_compute_subcontract_picking_ids"
    )

    def action_view_mrp(self):
        productions = self.subcontract_production_ids
        xmlid = "mrp.mrp_production_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if len(productions) > 1:
            action["domain"] = [("id", "in", productions.ids)]
        elif len(productions) == 1:
            action["views"] = [
                (self.env.ref("mrp.mrp_production_form_view").id, "form")
            ]
            action["res_id"] = productions.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def _compute_subcontract_production_count(self):
        for order in self:
            order.subcontract_production_count = len(order.subcontract_production_ids)

    def action_view_subcontract_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        subcontract_pick_ids = self.mapped("subcontract_picking_ids")
        # choose the view_mode accordingly
        if not subcontract_pick_ids or len(subcontract_pick_ids) > 1:
            result["domain"] = "[('id','in',%s)]" % (subcontract_pick_ids.ids)
        elif len(subcontract_pick_ids) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = subcontract_pick_ids.id
        return result

    def _compute_subcontract_picking_ids(self):
        for order in self:
            picking_ids = order.subcontract_production_ids.picking_ids
            order.subcontract_picking_ids = [(6, 0, picking_ids.ids)]
            order.subcontract_picking_count = len(picking_ids)
