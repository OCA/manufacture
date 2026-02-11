from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MultiQualityEditWizard(models.TransientModel):
    _name = "multi.quality.edit.wizard"
    _description = "Wizard for multi qc edition"

    quantitative_line_ids = fields.One2many(
        "multi.quality.edit.line",
        "wizard_id",
        domain="[('question_type', '=', 'quantitative')]",
    )
    qualitative_line_ids = fields.One2many(
        "multi.quality.edit.line",
        "wizard_id",
        domain="[('question_type', '=', 'qualitative')]",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self._context.get("active_ids")
        inspections = self.env["qc.inspection"].browse(active_ids)

        tests = inspections.mapped("test")
        if len(tests) != 1:
            raise ValidationError(
                self.env._(
                    "You should only select inspections linked to the same test."
                )
            )

        quantitative_line_ids = []
        qualitative_line_ids = []
        for insp in inspections:
            for quant_line in insp.inspection_lines.filtered(
                lambda line: line.question_type == "quantitative"
            ):
                quantitative_line_ids.append(
                    (
                        0,
                        0,
                        {
                            "inspection_id": insp.id,
                            "inspection_line_id": quant_line.id,
                            "quantitative_response": quant_line.quantitative_value,
                        },
                    )
                )
            for qual_line in insp.inspection_lines.filtered(
                lambda line: line.question_type == "qualitative"
            ):
                qualitative_line_ids.append(
                    (
                        0,
                        0,
                        {
                            "inspection_id": insp.id,
                            "inspection_line_id": qual_line.id,
                            "qualitative_response": qual_line.qualitative_value,
                        },
                    )
                )
        res["quantitative_line_ids"] = quantitative_line_ids
        res["qualitative_line_ids"] = qualitative_line_ids
        return res

    def action_save(self):
        for line in self.quantitative_line_ids:
            line.inspection_line_id.quantitative_value = line.quantitative_response
        for line in self.qualitative_line_ids:
            line.inspection_line_id.qualitative_value = line.qualitative_response
        return {"type": "ir.actions.act_window_close"}


class MultiQualityEditLine(models.TransientModel):
    _name = "multi.quality.edit.line"
    _description = "on line for display"

    wizard_id = fields.Many2one("multi.quality.edit.wizard", required=True)
    inspection_id = fields.Many2one("qc.inspection", string="Inspection", required=True)
    inspection_line_id = fields.Many2one(
        "qc.inspection.line", string="Ligne d'inspection", required=True
    )
    column_name = fields.Char(compute="_compute_column_name", string="Object")
    question_type = fields.Selection(
        related="inspection_line_id.question_type", string="Type de question"
    )
    question_name = fields.Char(related="inspection_line_id.name", string="Question")

    quantitative_response = fields.Float()
    qualitative_response = fields.Many2one("qc.test.question.value")
    qualitative_domain = fields.Binary(compute="_compute_qualitative_domain")

    def _compute_column_name(self):
        for line in self:
            line.column_name = (
                line.inspection_id.object_id.name
                if line.inspection_id.object_id
                else self.env._("Unknown")
            )

    def _compute_qualitative_domain(self):
        for line in self:
            line.qualitative_domain = [
                ("id", "in", line.inspection_line_id.possible_ql_values.ids)
            ]
