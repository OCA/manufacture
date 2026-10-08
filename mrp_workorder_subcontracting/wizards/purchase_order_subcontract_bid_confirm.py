from markupsafe import escape

from odoo import _, api, fields, models


class PurchaseOrderSubcontractBidWizard(models.TransientModel):
    _name = "purchase.order.subcontract.bid.wizard"
    _description = "Confirm Winning Subcontract Bid"

    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Winning Purchase Order",
        required=True,
        readonly=True,
    )
    competitor_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        string="Competing Purchase Orders",
        readonly=True,
    )
    summary_html = fields.Html(
        string="Summary",
        compute="_compute_summary_html",
        sanitize=False,
        readonly=True,
    )

    @api.depends("purchase_order_id", "competitor_order_ids")
    def _compute_summary_html(self):
        for wizard in self:
            items = []
            competitor_lines = (
                wizard.purchase_order_id._get_open_subcontract_bid_competitor_lines()
            )
            for order in wizard.competitor_order_ids:
                line_names = competitor_lines.filtered(
                    lambda line, order=order: line.order_id == order
                ).mapped("workorder_id.display_name")
                items.append(
                    f"<li>{escape(order.display_name)}: "
                    f"{escape(', '.join(line_names))}</li>"
                )
            wizard.summary_html = _(
                "<p>Confirming this purchase order will close the subcontracting "
                "bid for the work orders listed below.</p>"
                "<p>If a competing request for quotation contains only losing "
                "lines it will be cancelled. Otherwise the losing lines will be "
                "set to zero quantity and locked.</p>"
                "<ul>%s</ul>"
            ) % "".join(items)

    def action_confirm_bid(self):
        self.ensure_one()
        return self.purchase_order_id.with_context(
            skip_subcontract_bid_wizard=True
        ).button_confirm()
