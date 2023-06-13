# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_template_line",
        inverse_name="product_template",
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
                [("product_id", "in", self.product_variant_ids.ids)],
                ["product_id", "state"],
                ["product_id", "state"],
                lazy=False,
            )
        )
        product_data = {}
        for d in data:
            product_data.setdefault(d["product_id"][0], {}).setdefault(d["state"], 0)
            product_data[d["product_id"][0]][d["state"]] += d["__count"]
        for template in self:
            count_data_lst = [
                product_data.get(product.id, {})
                for product in template.product_variant_ids
            ]
            template.created_inspections = sum(
                sum(count_data.values()) for count_data in count_data_lst
            )
            template.passed_inspections = sum(
                count_data.get("success", 0) for count_data in count_data_lst
            )
            template.failed_inspections = sum(
                count_data.get("failed", 0) for count_data in count_data_lst
            )
            template.done_inspections = (
                template.passed_inspections + template.failed_inspections
            )

    def button_qc_inspection_per_product(self):
        self.ensure_one()
        return self.product_variant_ids._action_qc_inspection_per_product()
