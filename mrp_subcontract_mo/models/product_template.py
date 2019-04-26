# Copyright 2019 Le Filament (<http://www.le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Boolean = Whether product is subcontracted
    type_subcontracting = fields.Boolean(string="Is subcontracting service")
