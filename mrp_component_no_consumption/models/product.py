# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    skip_mo_consumption = fields.Boolean(
        string="Do not consume in Manufacturing Orders",
        help="If checked, this component will not reduce stock when used"
        " in Manufacturing Orders.",
    )
