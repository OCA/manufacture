from odoo import fields, models


class QcInspection(models.Model):
    """
    Quality Control Inspection with Manufacturer details
    """

    _inherit = "qc.inspection"

    manufacturer = fields.Many2one(
        related="product_id.manufacturer_id", string="Manufacturer"
    )
    manufacturer_code = fields.Char(
        related="product_id.manufacturer_pref", string="Manufacturer Code"
    )
