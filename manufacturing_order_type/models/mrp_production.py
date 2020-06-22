# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _default_mo_type_id(self):
        return self.env["manufacturing.order.type"].search(
            ["|", ("company_id", "=", False), ("company_id", "=", self.company_id.id)],
            limit=1,
        )

    mo_type_id = fields.Many2one(
        comodel_name="manufacturing.order.type",
        string="Type",
        ondelete="restrict",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self._default_mo_type_id(),
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        super().onchange_product_id()
        mo_type_id = self.product_id.mo_type_id or self.product_id.categ_id.mo_type_id
        if mo_type_id:
            self.mo_type_id = mo_type_id

    @api.onchange("mo_type_id")
    def _onchange_mo_type_id(self):
        for order in self:
            if order.mo_type_id.picking_type_id:
                order.picking_type_id = order.mo_type_id.picking_type_id

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/" and vals.get("mo_type_id"):
            mo_type = self.env["manufacturing.order.type"].browse(vals["mo_type_id"])
            if mo_type.sequence_id:
                vals["name"] = mo_type.sequence_id.next_by_id()
        return super().create(vals)
