# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, api, exceptions, fields, models, tools

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    auto_validate = fields.Boolean(
        string="Auto Validate",
        compute="_compute_auto_validate",
        store=True,
        states={"draft": [("readonly", False)]},
    )

    @api.constrains("bom_id", "auto_validate", "product_qty")
    def check_bom_auto_validate(self):
        for mo in self:
            qty_ok = (
                tools.float_compare(
                    mo.product_qty,
                    mo.bom_id.product_qty,
                    precision_rounding=mo.product_uom_id.rounding,
                )
                == 0
            )
            bypass_check = self.env.context.get("disable_check_mo_auto_validate")
            if bypass_check:
                return
            if mo.bom_id and mo.auto_validate and not qty_ok:
                raise exceptions.ValidationError(
                    _(
                        "The quantity to produce is restricted to {qty} "
                        "as the BoM is configured with the "
                        "'Order Auto Validation' option."
                    ).format(qty=mo.bom_id.product_qty)
                )

    @api.depends("bom_id.mo_auto_validation", "state")
    def _compute_auto_validate(self):
        for prod in self:
            if prod.state != "draft":
                # Avoid recomputing the value once the MO is confirmed.
                # e.g. if the value changes on the BOM but the MO was already confirmed,
                # or if the user forces another value while the MO is in draft,
                # we don't want to change the value after confirmation.
                continue
            prod.auto_validate = prod.bom_id.mo_auto_validation

    def _auto_validate_after_picking(self):
        self.ensure_one()
        if self.state == "progress":
            # If the MO is already in progress, we want to call the immediate
            # wizard to handle lot/serial number automatically (if any).
            action = self._action_generate_immediate_wizard()
            self._handle_wiz_mrp_immediate_production(action)
        res = self.button_mark_done()
        if res is True:
            return True
        res = self.handle_mark_done_result(res)
        # Each call might return a new wizard, loop until we satisfy all of them
        while isinstance(res, dict):
            res = self.handle_mark_done_result(res)

    def handle_mark_done_result(self, res):
        if res["res_model"] == "mrp.production":
            # MO has been processed and returned an action to open a backorder
            return True
        handler_name = "_handle_wiz_" + res["res_model"].replace(".", "_")
        handler = getattr(self, handler_name, None)
        if not handler:
            _logger.warning("'%s' wizard is not supported", res["res_model"])
            return True
        return handler(res)

    def _handle_wiz_mrp_immediate_production(self, action):
        wiz_model = self.env[action["res_model"]].with_context(
            **action.get("context", {})
        )
        wiz = wiz_model.create({})
        return wiz.process()

    def _handle_wiz_mrp_production_backorder(self, action):
        wiz_model = self.env[action["res_model"]].with_context(
            **action.get("context", {})
        )
        wiz = wiz_model.create({})
        return wiz.action_backorder()
