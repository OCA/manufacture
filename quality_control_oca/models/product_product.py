# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_line",
        inverse_name="product",
        string="Quality control triggers",
    )
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections"
    )
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections"
    )
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed"
    )

    def _compute_count_inspections(self):
        data = (
            self.env["qc.inspection"]
            .sudo()
            .read_group(
                [("product_id", "in", self.ids)],
                ["product_id", "state"],
                ["product_id", "state"],
                lazy=False,
            )
        )
        product_data = {}
        for d in data:
            product_data.setdefault(d["product_id"][0], {}).setdefault(d["state"], 0)
            product_data[d["product_id"][0]][d["state"]] += d["__count"]
        for product in self:
            count_data = product_data.get(product.id, {})
            product.created_inspections = sum(count_data.values())
            product.passed_inspections = count_data.get("success", 0)
            product.failed_inspections = count_data.get("failed", 0)
            product.done_inspections = (
                product.passed_inspections + product.failed_inspections
            )

    def button_qc_inspection_per_product(self):
        return self._action_qc_inspection_per_product()

    def _action_qc_inspection_per_product(self):
        product_ids = self.ids
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "quality_control_oca.action_qc_inspection"
        )
        domain = [("product_id", "in", product_ids)]
        qc_type = self.env.context.get("qc_type", "all")
        if qc_type == "done":
            domain.append(("state", "not in", ["draft", "waiting"]))
        elif qc_type == "passed":
            domain.append(("state", "=", "success"))
        elif qc_type == "failed":
            domain.append(("state", "=", "failed"))
        action["domain"] = domain
        if len(product_ids) == 1:
            context = ast.literal_eval(action.get("context"))
            context["default_object_id"] = "product.product,%s" % product_ids[0]
            action["context"] = context
        return action
