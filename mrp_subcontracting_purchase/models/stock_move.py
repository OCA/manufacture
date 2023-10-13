from odoo import _, api, models
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_subcontract_production(self):
        """Gets "Production orders" from the previous stock move when chaining them"""
        return self.filtered(lambda m: m.is_subcontract).move_orig_ids.production_id

    def _compute_display_assign_serial(self):
        """Generate multiple serial number and assigns them to stock move lines."""
        super(StockMove, self)._compute_display_assign_serial()
        for move in self:
            if not move.is_subcontract:
                continue
            productions = move._get_subcontract_production()
            if not productions or move.has_tracking != "serial":
                continue
            if (
                productions._has_tracked_component()
                or productions[:1].consumption != "strict"
            ):
                move.display_assign_serial = False

    def _compute_show_subcontracting_details_visible(self):
        """Compute if the action button in order to see moves raw is visible"""
        self.show_subcontracting_details_visible = False
        for move in self:
            if not move.is_subcontract and float_is_zero(
                move.quantity_done, precision_rounding=move.product_uom.rounding
            ):
                continue
            productions = move._get_subcontract_production()
            if not productions or (
                productions[:1].consumption == "strict"
                and not productions[:1]._has_tracked_component()
            ):
                continue
            move.show_subcontracting_details_visible = True

    def _compute_show_details_visible(self):
        """If the move is subcontract and the components are tracked. Then the
        show details button is visible.
        """
        res = super(StockMove, self)._compute_show_details_visible()
        for move in self:
            if not move.is_subcontract:
                continue
            productions = move._get_subcontract_production()
            if (
                not productions._has_tracked_component()
                and productions[:1].consumption == "strict"
            ):
                continue
            move.show_details_visible = True
        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("lot_name", "lot_id")
    def _onchange_serial_number(self):
        """Checks the correctness of the original location"""
        current_location_id = self.location_id
        res = super()._onchange_serial_number()
        subcontracting_location_id = self.company_id.subcontracting_location_id
        if (
            res
            and not self.lot_name
            and subcontracting_location_id == current_location_id
        ):
            # we want to avoid auto-updating source location in
            # this case + change the warning message
            self.location_id = current_location_id
            res["warning"]["message"] = (
                _(
                    """%s\n\nMake sure you validate or adapt the related resupply picking
                to your subcontractor in order to avoid inconsistencies in your stock.
                """
                )
                % res["warning"]["message"].split("\n\n", 1)[0]
            )
        return res
