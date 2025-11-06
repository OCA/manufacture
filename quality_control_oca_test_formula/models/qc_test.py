# Copyright 2025 Binhex - Ariel Brreiros
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import (
    datetime as safe_datetime,
)
from odoo.tools.safe_eval import (
    dateutil as safe_dateutil,
)
from odoo.tools.safe_eval import (
    pytz as safe_pytz,
)
from odoo.tools.safe_eval import (
    safe_eval,
)
from odoo.tools.safe_eval import (
    time as safe_time,
)

FORMULA_TEMPLATE = (
    "# Auto-compute runs when the inspection line is created or when the user\n"
    '# clicks "Recompute". Manual overrides keep their value until reset.\n'
    "# Assign the computed answer to the variable `result`.\n"
    "# Context variables:\n"
    "#   line        -> qc.inspection.line being filled\n"
    "#   inspection  -> parent qc.inspection\n"
    "#   test        -> qc.test definition\n"
    "#   question    -> qc.test.question definition\n"
    "#   env         -> Odoo environment\n"
    "#   datetime    -> Safe datetime helpers\n"
    "#   time        -> Safe subset of time module\n"
    "#   dateutil    -> Safe python-dateutil helpers\n"
    "#   timezone    -> Safe pytz.timezone helper\n"
    "# Expected results:\n"
    "#   * Quantitative -> float/int value\n"
    "#   * Qualitative  -> answer name string (match by name) or boolean to pick\n"
    "#                     the first value whose `ok` flag matches True/False.\n"
    "# Optional: assign `message` to append a log entry to internal notes.\n"
    "# Example: result = inspection.qty  # copy the ordered quantity\n"
    '#          message = f"Prefilled from {inspection.name}"\n'
)


def _contains_expression(code):
    """Return True when the string contains any non-comment expression."""
    for line in (code or "").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


class QcTestQuestion(models.Model):
    _inherit = "qc.test.question"

    auto_compute_formula = fields.Boolean(
        string="Auto-compute value",
        help=(
            "When enabled, inspection lines execute the formula to populate the "
            "answer."
        ),
    )
    formula_code = fields.Text(
        string="Formula",
        help=(
            "Python code that sets `result` with the value to use on inspection "
            "lines. Available variables: line, inspection, test, question, env, "
            "datetime, time, dateutil, timezone."
        ),
        default=FORMULA_TEMPLATE,
    )

    @api.constrains("formula_code", "auto_compute_formula")
    def _check_formula_syntax(self):
        """Ensure the stored formula is a valid Python expression."""
        for question in self:
            if not question.auto_compute_formula:
                continue
            if not question.formula_code:
                raise exceptions.ValidationError(
                    _("Formula is required when auto-compute is enabled on '%s'.")
                    % question.display_name
                )
            if not _contains_expression(question.formula_code):
                continue
            try:
                compile(question.formula_code, "<formula>", "exec")
            except SyntaxError as error:
                raise exceptions.ValidationError(
                    _("Invalid formula for '%(name)s': %(error)s")
                    % {
                        "name": question.display_name,
                        "error": error,
                    }
                ) from error

    @api.onchange("auto_compute_formula")
    def _onchange_auto_compute_formula(self):
        """Pre-fill template instructions when enabling auto-compute."""
        for question in self:
            if question.auto_compute_formula and not question.formula_code:
                question.formula_code = FORMULA_TEMPLATE

    def _formula_eval_context(self, inspection_line):
        """Build the evaluation context for a formula-enabled question."""
        return {
            "line": inspection_line,
            "inspection": inspection_line.inspection_id,
            "test": inspection_line.test_line.test,
            "question": inspection_line.test_line,
            "env": self.env,
            "datetime": safe_datetime,
            "time": safe_time,
            "dateutil": safe_dateutil,
            "timezone": safe_pytz.timezone,
            "result": None,
        }

    def _evaluate_formula(self, inspection_line):
        """Evaluate the formula and return (result, log_message)."""
        self.ensure_one()
        if not self.auto_compute_formula or not self.formula_code:
            return None, None
        if not _contains_expression(self.formula_code):
            return None, None
        context = self._formula_eval_context(inspection_line)
        try:
            safe_eval(
                self.formula_code,
                context,
                mode="exec",
                nocopy=True,
            )
        except Exception as error:
            raise exceptions.UserError(
                _("Error while evaluating formula for '%(name)s': %(error)s")
                % {
                    "name": self.display_name,
                    "error": error,
                }
            ) from error
        return context.get("result"), context.get("message")

    def _prepare_formula_update(self, inspection_line):
        """Return (values_dict, optional_log_message)."""
        self.ensure_one()
        if not self.auto_compute_formula:
            return {}, None
        result, log_message = self._evaluate_formula(inspection_line)
        if result is None:
            raise exceptions.UserError(
                _(
                    "Formula for '%(name)s' must assign a value to the variable "
                    "`result`."
                )
                % {"name": self.display_name}
            )
        handlers = {
            "quantitative": self._prepare_formula_update_quantitative,
            "qualitative": self._prepare_formula_update_qualitative,
        }
        handler = handlers.get(self.type)
        if not handler:
            return {}, log_message
        return handler(inspection_line, result), log_message

    def _prepare_formula_update_quantitative(self, inspection_line, result):
        """Build values dict for quantitative questions."""
        try:
            value = float(result)
        except (TypeError, ValueError) as error:
            raise exceptions.UserError(
                _("Formula for '%(name)s' must return a number, got %(type)s.")
                % {
                    "name": self.display_name,
                    "type": type(result).__name__,
                }
            ) from error
        precision = inspection_line._get_quality_precision()
        if float_compare(value, 0.0, precision_digits=precision) == 0:
            value = 0.0
        updates = {"quantitative_value": value}
        if inspection_line.test_uom_id:
            updates.setdefault("uom_id", inspection_line.test_uom_id.id)
        return updates

    def _prepare_formula_update_qualitative(self, inspection_line, result):
        """Build values dict for qualitative questions."""
        value_record = self._resolve_qualitative_value(inspection_line, result)
        if not value_record:
            return {}
        return {"qualitative_value": value_record.id}

    def _resolve_qualitative_value(self, inspection_line, result):
        """Resolve the qualitative value returned by the formula."""
        candidates = inspection_line.possible_ql_values
        if not candidates:
            return False
        record = candidates
        if isinstance(result, str) and result:
            record = candidates.filtered(lambda r: r.name == result)
        elif isinstance(result, bool):
            record = candidates.filtered(lambda r: bool(r.ok) is result)
        else:
            return False
        return record[0] if record else False
