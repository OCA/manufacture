# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    remind_qc = fields.Boolean(
        string="Remind Quality Control",
        help="If selected, notify to perform Quality Control on this product when scheduled",
    )

    auto_scrap = fields.Boolean(
        string="Scrap Automatically",
        help="If selected, automatically scraps this product when inspections fail",
    )
