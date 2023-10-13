from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    subcontracting_resupply_picking_count = fields.Integer(
        "Count of Subcontracting Resupply",
        compute="_compute_subcontracting_resupply_picking_count",
        help="Count of Subcontracting Resupply for component",
    )

    @api.depends("order_line.move_ids")
    def _compute_subcontracting_resupply_picking_count(self):
        for purchase in self:
            purchase.subcontracting_resupply_picking_count = len(
                purchase._get_subcontracting_resupplies()
            )

    def action_view_subcontracting_resupply(self):
        return self._get_action_view_picking(self._get_subcontracting_resupplies())

    def _get_subcontracting_resupplies(self):
        return self.order_line.move_ids.filtered(lambda m: m.is_subcontract).mapped(
            "move_orig_ids.production_id.picking_ids"
        )

    @api.depends("order_line.move_dest_ids.group_id.mrp_production_ids")
    def _compute_mrp_production_count(self):
        for purchase in self:
            purchase.mrp_production_count = len(purchase._get_mrp_productions())

    def _get_mrp_productions(self, **kwargs):
        productions = (
            self.order_line.move_dest_ids.group_id.mrp_production_ids
            | self.order_line.move_ids.move_dest_ids.group_id.mrp_production_ids
        )
        if kwargs.get("remove_archived_picking_types", True):
            productions = productions.filtered(
                lambda production: production.with_context(
                    active_test=False
                ).picking_type_id.active
            )
        return productions

    def action_view_picking(self):
        return self._get_action_view_picking(self.picking_ids)

    def _get_action_view_picking(self, pickings):
        """This function returns an action that display existing picking orders
        of given purchase order ids. When only one found, show the picking immediately.
        """
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # override the context to get rid of the default filtering on operation type
        result["context"] = {
            "default_partner_id": self.partner_id.id,
            "default_origin": self.name,
            "default_picking_type_id": self.picking_type_id.id,
        }
        # choose the view_mode accordingly
        if not pickings or len(pickings) > 1:
            result["domain"] = [("id", "in", pickings.ids)]
        elif len(pickings) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            form_view = [(res and res.id or False, "form")]
            result.update(
                {
                    "views": form_view
                    + [
                        (state, view)
                        for state, view in result.get("views", [])
                        if view != "form"
                    ],
                    "res_id": pickings.id,
                }
            )
        return result

    def _get_destination_location(self):
        """Returns destination location for subcontractor"""
        self.ensure_one()
        if not self.dest_address_id or self.sale_order_count:
            return super(PurchaseOrder, self)._get_destination_location()

        mrp_production_ids = self._get_mrp_productions(
            remove_archived_picking_types=False
        )

        if (
            mrp_production_ids
            and self.dest_address_id in mrp_production_ids.bom_id.subcontractor_ids
        ):
            return self.dest_address_id.property_stock_subcontractor.id

        in_bom_products = False
        not_in_bom_products = self.env["purchase.order.line"]
        for order_line in self.order_line:
            if any(
                bom_line.bom_id.type == "subcontract"
                and self.dest_address_id in bom_line.bom_id.subcontractor_ids
                for bom_line in order_line.product_id.bom_line_ids.filtered(
                    lambda line: line.company_id == self.company_id
                )
            ):
                in_bom_products = True
            elif not order_line.display_type:
                not_in_bom_products |= order_line
        if in_bom_products and not_in_bom_products:
            raise UserError(
                _(
                    """It appears some components in this RFQ are not meant for subcontracting.
                    Please create a separate order for these."""
                )
                + "\n\n"
                + "\n".join(not_in_bom_products.mapped("name"))
            )
        elif in_bom_products:
            return self.dest_address_id.property_stock_subcontractor.id
        return super()._get_destination_location()
