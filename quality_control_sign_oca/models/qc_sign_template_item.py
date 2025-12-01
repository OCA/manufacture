# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class QcSignTemplateItem(models.Model):
    _name = "qc.sign.template.item"
    _description = "Quality Control Sign Template Item"

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    report_id = fields.Many2one(
        "ir.actions.report",
        string="Report",
        required=True,
        domain="[('model', '=', 'qc.inspection'), ('report_type', '=', 'qweb-pdf')]",
    )

    role_id = fields.Many2one(
        "sign.oca.role",
        string="Sign Role",
        required=True,
        help="Role that will sign (Customer, Employee...).",
    )

    page = fields.Integer(
        default=1,
        required=True,
    )

    position_x = fields.Float(required=True)

    position_y = fields.Float(required=True)

    width = fields.Float()

    height = fields.Float()
