# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_batch_propagate = fields.Boolean(
        string="MRP Batch Propagate",
        help="This product will propagate BOM information"
        " through manufacturing batches",
    )

    mrp_batch_propagate_computed = fields.Boolean(
        string="MRP Batch Propagate (Computed)",
        help="Computed MRP batch propagate setting from template or category",
        compute="_compute_mrp_batch_propagate",
    )

    @api.depends("mrp_batch_propagate", "categ_id.mrp_batch_propagate")
    def _compute_mrp_batch_propagate(self):
        """Compute MRP batch propagate setting from template or category"""
        for template in self:
            if template.mrp_batch_propagate:
                template.mrp_batch_propagate_computed = True
            else:
                template.mrp_batch_propagate_computed = bool(
                    template.categ_id.mrp_batch_propagate
                )
