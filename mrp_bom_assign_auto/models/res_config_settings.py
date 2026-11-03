from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Add option for user to decide bom auto check by
    virtual_available o free_qty"""

    _inherit = "res.config.settings"

    bom_stock_check = fields.Selection(
        selection=[("virtual_available", "Vitual Available"), ("free_qty", "Free Qty")],
        default="free_qty",
        config_parameter="mrp_bom_assign_auto.bom_stock_check",
    )
