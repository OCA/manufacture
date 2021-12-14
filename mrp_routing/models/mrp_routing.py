# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class MrpRouting(models.Model):

    _name = "mrp.routing"
    _description = "Manufacturing Routing"

    name = fields.Char("Routing", required=True)
    active = fields.Boolean(
        "Active",
        default=True,
        help="If the active field is set to False, "
        "it will allow you to hide the routing without removing it.",
    )
    code = fields.Char(
        "Reference", copy=False, default=lambda self: _("New"), readonly=True
    )
    note = fields.Text("Description")
    operation_ids = fields.Many2many(
        comodel_name="mrp.routing.workcenter.template", string="Operations"
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    bom_ids = fields.One2many(
        comodel_name="mrp.bom",
        inverse_name="routing_id",
        string="Boms",
        required=False,
        copy=False,
    )

    @api.model
    def create(self, vals):
        if "code" not in vals or vals["code"] == _("New"):
            vals["code"] = self.env["ir.sequence"].next_by_code("mrp.routing") or _(
                "New"
            )
        return super(MrpRouting, self).create(vals)

    def write(self, values):
        res = super(MrpRouting, self).write(values)
        if "operation_ids" in values:
            for rec in self:
                for bom in rec.bom_ids:
                    operations_not_synced = (
                        rec.operation_ids - bom.operation_ids.mapped("template_id")
                    )
                    for operation in operations_not_synced:
                        operation.create_operation_from_template(bom)
                    operations_to_delete = bom.operation_ids.filtered(
                        lambda x: x.template_id.id not in rec.operation_ids.ids
                    )
                    if operations_to_delete:
                        operations_to_delete.unlink()
        return res
