# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_qty_net = fields.Float(
        string="Net quantity",
        help="Quantity after process",
        digits="Product Unit of Measure",
    )
    loss_percentage = fields.Float(
        string="Loss %",
        help="Percentage loss during process",
        digits=(16, 2),
    )
    diff_product_qty_gross_net = fields.Float(
        digits="Product Price",
        compute="_compute_diff_product_qty_gross_net",
    )

    # Functions to change product fields
    def calculate_qty_net_theoretical(self, product_qty_gross, loss_percentage):
        return (1 - loss_percentage / 100) * product_qty_gross

    @api.depends("product_qty", "product_qty_net", "loss_percentage")
    def _compute_diff_product_qty_gross_net(self):
        for bom_line in self:
            _bom_line_qty_net_theorical = self.calculate_qty_net_theoretical(
                bom_line.product_qty, bom_line.loss_percentage
            )
            _diff_product_qty_gross_net = round(
                (bom_line.product_qty_net - _bom_line_qty_net_theorical), 2
            )
            bom_line.diff_product_qty_gross_net = _diff_product_qty_gross_net

    # Two buttons to handle two cases : you base your price on net qty or gross qty
    def set_product_qty_net(self):
        for bom_line in self.filtered(lambda x: x.product_qty):
            bom_line.product_qty_net = self.calculate_qty_net_theoretical(
                bom_line.product_qty, bom_line.loss_percentage
            )

    def set_product_qty_gross(self):
        for bom_line in self.filtered(lambda x: x.product_qty_net):
            if bom_line.loss_percentage == 100:
                raise UserError(
                    _(
                        "Setting gross quantity with 100% loss makes no sense.\n"
                        "Change this value."
                    )
                )
            else:
                bom_line.product_qty = bom_line.product_qty_net / (
                    1 - bom_line.loss_percentage / 100
                )

    # If you change mandatory field product_qty (gross qty), the net quantity adapts
    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        for bom_line in self:
            bom_line.product_qty_net = bom_line.product_qty
