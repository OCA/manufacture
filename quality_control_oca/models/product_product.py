# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# Copyright 2023 Solvos Consultoría Informática, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


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
