# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class QcTest(models.Model):
    """
    A test is a group of questions along with the values that make them valid.
    """

    _name = "qc.test"
    _description = "Quality control test"
    _inherit = "mail.thread"

    def object_selection_values(self):
        return set()

    @api.onchange("type")
    def onchange_type(self):
        if self.type == "generic":
            self.object_id = False

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, translate=True)
    test_lines = fields.One2many(
        comodel_name="qc.test.question",
        inverse_name="test",
        string="Questions",
        copy=True,
    )
    object_id = fields.Reference(
        string="Reference object",
        selection="object_selection_values",
    )
    fill_correct_values = fields.Boolean(string="Pre-fill with correct values")
    type = fields.Selection(
        [("generic", "Generic"), ("related", "Related")],
        required=True,
        default="generic",
    )
    category = fields.Many2one(comodel_name="qc.test.category")
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )


class QcTestQuestion(models.Model):
    """Each test line is a question with its valid value(s)."""

    _name = "qc.test.question"
    _description = "Quality control question"
    _order = "sequence, id"

    @api.constrains("ql_values")
    def _check_valid_answers(self):
        for tc in self:
            if (
                tc.type == "qualitative"
                and tc.ql_values
                and not tc.ql_values.filtered("ok")
            ):
                raise exceptions.ValidationError(
                    _(
                        "Question '%s' is not valid: "
                        "you have to mark at least one value as OK."
                    )
                    % tc.name_get()[0][1]
                )

    @api.constrains("min_value", "max_value")
    def _check_valid_range(self):
        for tc in self:
            if tc.type == "quantitative" and tc.min_value > tc.max_value:
                raise exceptions.ValidationError(
                    _(
                        "Question '%s' is not valid: "
                        "minimum value can't be higher than maximum value."
                    )
                    % tc.name_get()[0][1]
                )

    sequence = fields.Integer(required=True, default="10")
    test = fields.Many2one(comodel_name="qc.test")
    name = fields.Char(required=True, translate=True)
    type = fields.Selection(
        [("qualitative", "Qualitative"), ("quantitative", "Quantitative")],
        required=True,
    )
    ql_values = fields.One2many(
        comodel_name="qc.test.question.value",
        inverse_name="test_line",
        string="Qualitative values",
        copy=True,
    )
    notes = fields.Text()
    min_value = fields.Float(string="Min", digits="Quality Control")
    max_value = fields.Float(string="Max", digits="Quality Control")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom")


class QcTestQuestionValue(models.Model):
    _name = "qc.test.question.value"
    _description = "Possible values for qualitative questions."

    test_line = fields.Many2one(comodel_name="qc.test.question", string="Test question")
    name = fields.Char(required=True, translate=True)
    ok = fields.Boolean(
        string="Correct answer?",
        help="When this field is marked, the answer is considered correct.",
    )
