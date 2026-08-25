from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    sub_delivery_workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Subcontract Workorder (Is delivery)",
        readonly=True,
        copy=True,
    )
    sub_return_workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Subcontract Workorder (Is return)",
        readonly=True,
        copy=True,
    )
    sub_purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Subcontractor purchase order line",
        readonly=True,
        copy=True,
        index=True,
    )
    sub_origin_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Subcontract Origin Move",
        readonly=True,
        copy=True,
        index=True,
    )
    sub_component_workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Subcontract Component Work Order",
        copy=False,
        index=True,
        check_company=True,
        help=(
            "Work order used by the subcontracting flow to send this component "
            "to the subcontractor. It is taken from the BoM operation."
        ),
    )
    subcontracting_flow = fields.Selection(
        selection=[
            ("parts", "Sending Parts"),
            ("finished", "Sending Finished Product"),
        ],
        string="Subcontracting Supply Method",
        compute="_compute_subcontract_links",
        store=True,
    )
    # Easy navigation fields
    sub_workorder_id = fields.Many2one(
        comodel_name="mrp.workorder",
        string="Subcontract Work Order",
        compute="_compute_subcontract_links",
        store=True,
        readonly=True,
    )
    sub_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Subcontract Manufacturing Order",
        compute="_compute_subcontract_links",
        store=True,
        readonly=True,
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super()._prepare_merge_moves_distinct_fields()
        fields += [
            "sub_delivery_workorder_id",
            "sub_return_workorder_id",
            "sub_purchase_line_id",
            "sub_origin_move_id",
            "sub_component_workorder_id",
        ]
        return fields

    @api.depends("sub_delivery_workorder_id", "sub_return_workorder_id")
    def _compute_subcontract_links(self):
        for move in self:
            workorder = move.sub_delivery_workorder_id or move.sub_return_workorder_id
            move.sub_workorder_id = workorder
            move.subcontracting_flow = (
                workorder.subcontracting_flow if workorder else False
            )
            move.sub_production_id = workorder.production_id if workorder else False

    @api.constrains("sub_component_workorder_id", "raw_material_production_id")
    def _check_sub_component_workorder_id(self):
        for move in self.filtered("sub_component_workorder_id"):
            workorder = move.sub_component_workorder_id
            if not workorder.subcontract_ok:
                raise ValidationError(
                    _(
                        "The subcontract component work order must be configured "
                        "as subcontracted."
                    )
                )
            if workorder.production_id != move.raw_material_production_id:
                raise ValidationError(
                    _(
                        "The subcontract component work order must belong to the "
                        "same manufacturing order as the component move."
                    )
                )

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        vals.update(
            {
                "sub_delivery_workorder_id": self.sub_delivery_workorder_id.id,
                "sub_return_workorder_id": self.sub_return_workorder_id.id,
                "sub_purchase_line_id": self.sub_purchase_line_id.id,
                "sub_origin_move_id": self.id,
            }
        )
        return vals

    def action_open_subcontract_picking(self):
        self.ensure_one()
        if not self.picking_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.picking_id.display_name,
            "res_model": "stock.picking",
            "view_mode": "form",
            "views": [(self.env.ref("stock.view_picking_form").id, "form")],
            "res_id": self.picking_id.id,
        }
