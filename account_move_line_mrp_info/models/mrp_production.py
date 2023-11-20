# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from ast import literal_eval

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line", inverse_name="mrp_production_id", copy=False
    )

    def view_journal_items(self):
        self.ensure_one()
        domain = [
            (
                "id",
                "in",
                (self.account_move_line_ids).ids,
            )
        ]
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_move_line_mrp_info.action_view_journal_items"
        )
        context = literal_eval(action["context"])
        context.update(self.env.context)
        context["no_at_date"] = True
        context["search_default_group_by_product_id"] = False
        return dict(action, domain=domain, context=context)


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line", inverse_name="unbuild_id", copy=False
    )

    def view_journal_items(self):
        self.ensure_one()
        domain = [
            (
                "id",
                "in",
                (self.account_move_line_ids).ids,
            )
        ]
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_move_line_mrp_info.action_view_journal_items"
        )
        context = literal_eval(action["context"])
        context.update(self.env.context)
        context["no_at_date"] = True
        context["search_default_group_by_product_id"] = False
        return dict(action, domain=domain, context=context)
