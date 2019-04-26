# Copyright 2019 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    # Boolean = Whether related product is subcontracted
    # Used to change domain / context when selecting subcontractor in view
    type_subcontracting = fields.Boolean(
        related="product_tmpl_id.type_subcontracting")
