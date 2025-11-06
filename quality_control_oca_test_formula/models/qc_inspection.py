# Copyright 2025 Binhex - Ariel Brreiros
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    has_auto_compute_formula_lines = fields.Boolean(
        compute="_compute_has_auto_compute_formula_lines",
        help=(
            "True when inspection lines with auto-compute formulas need "
            "recomputation."
        ),
    )

    @api.depends(
        "inspection_lines.auto_compute_formula",
        "inspection_lines.manual_override",
    )
    def _compute_has_auto_compute_formula_lines(self):
        for inspection in self:
            inspection.has_auto_compute_formula_lines = bool(
                inspection.inspection_lines.filtered(
                    lambda line: line.auto_compute_formula and line.manual_override
                )
            )

    def action_recompute_formula_lines(self):
        for inspection in self:
            lines = inspection.inspection_lines.filtered(
                lambda line: line.auto_compute_formula and line.manual_override
            )
            for line in lines:
                line._apply_formula_auto_value()
        return True


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    auto_compute_formula = fields.Boolean(
        related="test_line.auto_compute_formula",
        string="Auto-compute",
        store=True,
        readonly=True,
    )
    auto_computed = fields.Boolean(
        string="Auto-computed",
        default=False,
        copy=False,
        help="True when the answer was last populated by the formula.",
    )
    manual_override = fields.Boolean(
        string="Manual override",
        default=False,
        copy=False,
        help="Set to True when the user edited the answer after an auto-compute.",
    )

    @api.depends(
        "question_type",
        "uom_id",
        "test_uom_id",
        "max_value",
        "min_value",
        "quantitative_value",
        "qualitative_value",
        "possible_ql_values",
        "inspection_id.state",
    )
    def _compute_quality_test_check(self):
        for line in self:
            if (
                line.inspection_id.state == "ready"
                and line.auto_compute_formula
                and not line.auto_computed
                and not line.manual_override
            ):
                line._apply_formula_auto_value()
        return super()._compute_quality_test_check()

    def write(self, vals):
        tracked = {"quantitative_value", "qualitative_value"}
        reset_needed = bool(tracked & vals.keys()) and not self.env.context.get(
            "from_formula_auto_compute"
        )
        new_vals = dict(vals)
        if reset_needed:
            new_vals["auto_computed"] = False
            new_vals["manual_override"] = True
        return super().write(new_vals)

    def _apply_formula_auto_value(self):
        self.ensure_one()
        values, log_message = self.test_line._prepare_formula_update(self)
        if not values:
            return False
        values["auto_computed"] = True
        values["manual_override"] = False
        self.with_context(from_formula_auto_compute=True).write(values)
        if log_message:
            self._append_formula_log(log_message)
        return True

    def _get_quality_precision(self):
        self.ensure_one()
        try:
            dp = self.env.ref("quality_control_oca.decimal_quality_control")
            return dp.digits or 2
        except ValueError:
            return 2

    def _append_formula_log(self, message):
        """Append a formatted log entry to the inspection internal notes."""
        self.ensure_one()
        inspection = self.inspection_id
        if not inspection:
            return
        try:
            message_text = str(message)
        except Exception:
            return
        if not message_text:
            return
        timestamp = fields.Datetime.now()
        block = _("LOG: {timestamp}\n--------------------------\n{message}").format(
            timestamp=timestamp, message=message_text
        )
        existing = (inspection.internal_notes or "").rstrip()
        note = f"{existing}\n\n{block}" if existing else block
        inspection.write({"internal_notes": note})
