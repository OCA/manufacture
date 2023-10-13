# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    subcontracting_has_been_recorded = fields.Boolean("Has been recorded", copy=False)

    def subcontracting_record_component(self):
        """Returns subcontracting issues

        Since we don't have a subcontracting_has_been_recorded field in version 14.0,
        we need to add functionality related to this field
        """
        self.ensure_one()
        self._check_exception_subcontracting_record_component()
        consumption_issues = self._get_consumption_issues()
        if consumption_issues:
            return self._action_generate_consumption_wizard(consumption_issues)
        self._update_finished_move()
        self.subcontracting_has_been_recorded = True
        if self._get_quantity_produced_issues():
            return self._has_quantity_issues()
        return {"type": "ir.actions.act_window_close"}

    def _check_exception_subcontracting_record_component(self):
        """Check exceptions subcontracting component"""
        if not self._get_subcontract_move():
            raise UserError(_("This MO isn't related to a subcontracted move"))
        if float_is_zero(
            self.qty_producing, precision_rounding=self.product_uom_id.rounding
        ):
            return {"type": "ir.actions.act_window_close"}
        if self.product_tracking != "none" and not self.lot_producing_id:
            raise UserError(
                _("You must enter a serial number for %s") % self.product_id.name
            )
        smls = self.move_raw_ids.move_line_ids.filtered(
            lambda s: s.tracking != "none" and not s.lot_id
        )
        if smls:
            sml = fields.first(smls)
            raise UserError(
                _("You must enter a serial number for each line of %s")
                % sml.product_id.display_name
            )
        if self.move_raw_ids and not any(self.move_raw_ids.mapped("quantity_done")):
            raise UserError(
                _(
                    """You must indicate a non-zero amount
                    consumed for at least one of your components"""
                )
            )

    def _has_quantity_issues(self):
        """Returns action with issues"""
        backorder = self._generate_backorder_productions(close_mo=False)
        # No qty to consume to avoid propagate additional move
        # TODO avoid : stock move created in backorder with 0 as qty
        backorder.move_raw_ids.filtered(lambda m: m.additional).product_uom_qty = 0.0
        backorder.qty_producing = backorder.product_qty
        backorder._set_qty_producing()
        self.product_qty = self.qty_producing
        action = (
            self._get_subcontract_move()
            .filtered(lambda m: m.state not in ("done", "cancel"))
            ._action_record_components()
        )
        action.update(res_id=backorder.id)
        return action

    def _pre_button_mark_done(self):
        return (
            True
            if self._get_subcontract_move()
            else super(MrpProduction, self)._pre_button_mark_done()
        )

    def _subcontracting_filter_to_done(self):
        # OVERRIDE, to add condition 'not mo.subcontracting_has_been_recorded',
        # which checks whether the subcontracting has been recorded or not

        def filter_in(mo):
            return not (
                mo.state in ("done", "cancel")
                or not mo.subcontracting_has_been_recorded
                or float_is_zero(
                    mo.qty_producing, precision_rounding=mo.product_uom_id.rounding
                )
                or not all(
                    line.lot_id
                    for line in mo.move_raw_ids.filtered(
                        lambda sm: sm.has_tracking != "none"
                    ).move_line_ids
                )
                or mo.product_tracking != "none"
                and not mo.lot_producing_id
            )

        return self.filtered(filter_in)

    def _has_been_recorded(self):
        """Checks for records in subcontracting production"""
        self.ensure_one()
        return self.state in ("cancel", "done") or self.subcontracting_has_been_recorded

    def _has_tracked_component(self):
        """Checks the component for tracking in the stock"""
        return any(m.has_tracking != "none" for m in self.move_raw_ids)

    def _get_subcontract_move(self):
        """Returns destination for subcontract"""
        return self.move_finished_ids.move_dest_ids.filtered(lambda m: m.is_subcontract)
