from odoo import fields, models


class StockWarehouseOrderPoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    supplier_id = fields.Many2one(comodel_name="product.supplierinfo")
