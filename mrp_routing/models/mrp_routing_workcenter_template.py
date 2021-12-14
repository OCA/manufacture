# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

FIELDS_TO_SYNC = [
    "name",
    "workcenter_id",
    "sequence",
    "worksheet_type",
    "note",
    "worksheet",
    "worksheet_google_slide",
    "time_mode",
    "time_mode_batch",
    "time_cycle_manual",
    "on_template_change",
]


class MrpRoutingWorkcenterTemplate(models.Model):

    _name = "mrp.routing.workcenter.template"
    _description = "Template Work Center Usage"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char("Operation", required=True)
    workcenter_id = fields.Many2one(
        "mrp.workcenter", "Work Center", required=True, check_company=True
    )
    sequence = fields.Integer(
        "Sequence",
        default=100,
        help="Gives the sequence order when displaying a list of routing Work Centers.",
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    worksheet_type = fields.Selection(
        [("pdf", "PDF"), ("google_slide", "Google Slide"), ("text", "Text")],
        string="Work Sheet",
        default="text",
        help="Defines if you want to use a PDF " "or a Google Slide as work sheet.",
    )
    note = fields.Text("Description", help="Text worksheet description")
    worksheet = fields.Binary("PDF")
    worksheet_google_slide = fields.Char(
        "Google Slide",
        help="Paste the url of your Google Slide. "
        "Make sure the access to the document is public.",
    )
    time_mode = fields.Selection(
        [
            ("auto", "Compute based on tracked time"),
            ("manual", "Set duration manually"),
        ],
        string="Duration Computation",
        default="manual",
    )
    time_mode_batch = fields.Integer("Based on", default=10)
    time_cycle_manual = fields.Float(
        "Manual Duration",
        default=60,
        help="Time in minutes:"
        "- In manual mode, time used"
        "- In automatic mode, "
        "supposed first time when there aren't any work orders yet",
    )
    operation_ids = fields.One2many(
        comodel_name="mrp.routing.workcenter",
        inverse_name="template_id",
        string="Operations",
        required=False,
        copy=False,
    )
    on_template_change = fields.Selection(
        string="On template change?",
        selection=[
            ("nothing", "Do nothing"),
            ("sync", "Sync"),
        ],
        required=False,
        default="sync",
    )
    routing_ids = fields.Many2many(comodel_name="mrp.routing", string="Routings")

    def create_operation_from_template(self, bom):
        operation_model = self.env["mrp.routing.workcenter"]
        for operation in self:
            operation_data = operation.read(FIELDS_TO_SYNC, load="_classic_write")[0]
            operation_data.update(
                {
                    "bom_id": bom.id,
                    "template_id": operation.id,
                    "on_template_change": "sync",
                }
            )
            operation_model.create(operation_data)

    @api.model_create_multi
    def create(self, values):
        recs = super(MrpRoutingWorkcenterTemplate, self).create(values)
        for rec in self:
            for bom in rec.mapped("routing_ids.bom_ids"):
                rec.create_operation_from_template(bom)
        return recs

    def unlink(self):
        for rec in self:
            synced_records = rec.operation_ids.filtered(
                lambda x: x.on_template_change == "sync"
            )
            if synced_records:
                synced_records.unlink()
        return super(MrpRoutingWorkcenterTemplate, self).unlink()

    def write(self, values):
        res = super(MrpRoutingWorkcenterTemplate, self).write(values)
        current_field_changes = []
        for field_name in FIELDS_TO_SYNC:
            if field_name in values.keys():
                current_field_changes.append(field_name)
        if current_field_changes:
            for rec in self.filtered(lambda x: x.operation_ids):
                to_write_data = rec.read(current_field_changes)[0]
                to_write = rec.operation_ids.filtered(
                    lambda x: x.on_template_change == "sync"
                )
                if to_write:
                    to_write.write(to_write_data)
        return res
