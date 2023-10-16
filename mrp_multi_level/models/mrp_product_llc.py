# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class MrpProductLlc(models.Model):
    _name = "mrp.product.llc"
    _description = "MRP Product LLC"

    product_id = fields.Many2one('product.product', "Product", required=True, ondelete='cascade')
    llc = fields.Integer(string="Low Level Code", default=0, index=True)

    _sql_constraints = [
        (
            "product_unique",
            "unique(product_id)",
            "The MRP Product LLC must be unique."
        ),
    ]


