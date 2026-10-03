# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    mrp_batch_propagate = fields.Boolean(
        string="MRP Batch Propagate",
        help="Products in this category will propagate BOM information"
        " through manufacturing batches",
    )
