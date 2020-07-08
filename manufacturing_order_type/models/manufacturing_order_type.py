# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ManufacturingOrderType(models.Model):
    _name = "manufacturing.order.type"
    _description = "Type of manufacturing order"
    _order = "sequence"

    @api.model
    def _get_domain_sequence_id(self):
        mrp_seq = (
            self.env["stock.picking.type"]
            .search([("code", "=", "mrp_operation")])
            .mapped("sequence_id")
        )
        return [
            "&",
            "|",
            ("code", "=", "mrp.production"),
            ("id", "in", mrp_seq.ids),
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ]

    @api.model
    def _default_sequence_id(self):
        picking_type_id = self.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        return picking_type_id.sequence_id.id

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description", translate=True)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Entry Sequence",
        copy=False,
        domain=_get_domain_sequence_id,
        default=lambda self: self._default_sequence_id(),
        required=True,
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]",
    )

    # @api.constraints('company_id', 'picking_type_id')
    # def _check_company_id(self):
    #     for r in self:
    #         if r.company_id == record.picking_type_id:
    #             raise ValidationError(
    #                 _("Amount cannot be negative"))
