from ast import literal_eval

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_view_stock_valuation_layers(self):
        self.ensure_one()
        domain = [
            (
                "id",
                "in",
                (
                    self.produce_line_ids + self.consume_line_ids
                ).stock_valuation_layer_ids.ids,
            )
        ]
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_account.stock_valuation_layer_action"
        )
        context = literal_eval(action["context"])
        context.update(self.env.context)
        context["no_at_date"] = True
        context["search_default_group_by_product_id"] = False
        return dict(action, domain=domain, context=context)
