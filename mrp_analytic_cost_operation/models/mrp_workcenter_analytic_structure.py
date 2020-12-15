# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkCenterAnalyticStructure(models.Model):
    _name = "mrp.workcenter.analytic.structure"
    _description = "Work center analytic structure"
    _rec_name = "work_center_id"

    work_center_id = fields.Many2one(
        "mrp.workcenter",
        string="Work Center",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    factor = fields.Float(
        string="Factor",
    )
