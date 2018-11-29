# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_production_request = fields.Boolean(
        string='Manufacturing Request', help="Check this box to generate "
        "manufacturing request instead of generating manufacturing orders "
        "from procurement.", default=False)
