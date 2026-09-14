# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        readonly=True,
        store=True,
        related="sale_line_id.order_id",
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Customer",
        store=True,
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date", string="Commitment Date", store=True
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref",
        string="Customer Reference",
        store=True,
    )

    def action_merge(self):
        """Retain the sale information when merging manufacturing orders.

        The standard ``action_merge`` creates a brand new manufacturing order
        and cancels the source ones, which drops the link to the originating
        sale order. When every merged order comes from the same sale order
        line, propagate it to the resulting order so that ``sale_id``,
        ``partner_id`` and ``client_order_ref`` (all related to
        ``sale_line_id``) are kept. If the orders come from different sale
        order lines (or none), nothing is propagated.
        """
        sale_lines = self.mapped("sale_line_id")
        keep_sale_line = (
            sale_lines
            if len(sale_lines) == 1
            and all(production.sale_line_id == sale_lines for production in self)
            else self.env["sale.order.line"]
        )
        action = super().action_merge()
        if keep_sale_line and isinstance(action, dict) and action.get("res_id"):
            self.browse(action["res_id"]).sale_line_id = keep_sale_line.id
        return action
