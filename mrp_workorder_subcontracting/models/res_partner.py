from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_stock_subcontract_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Subcontract Location",
        copy=False,
        domain=[("usage", "=", "internal")],
        help=(
            "Subcontracting location to be used for managing the flow of parts "
            "sent and finished products returned from this supplier."
        ),
    )
    property_stock_virtual_subcontract_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Subcontract Virtual Location",
        copy=False,
        domain=[("usage", "=", "production")],
        help=(
            "Virtual subcontracting location to be used in cases where the "
            "finished product is shipped out and returned with the same item code."
        ),
    )
