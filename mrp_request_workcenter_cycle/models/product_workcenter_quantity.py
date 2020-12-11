# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductWorkcenterQuantity(models.Model):
    _name = "product.workcenter.quantity"
    _description = "Quantity that can be produced with a workcenter cycle"

    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter", string="Workcenter")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_qty = fields.Float(
        default=1, help="Quantity of the product that the workcenter use in a cycle."
    )
    workcenter_cycle_no = fields.Float(
        string="Cycle Number",
        default=1,
        help="Default number of cycles for the workcenter set for "
        "Manufacturing Request of this product.\n",
    )

    _sql_constraints = [
        (
            "product_workcenter_unique",
            "UNIQUE(workcenter_id,product_id)",
            "Workcenter field must be unique by product",
        )
    ]
