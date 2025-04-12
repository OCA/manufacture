#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr


class MRPBomLine(models.Model):
    _inherit = "mrp.bom.line"

    quantity_formula = fields.Text(
        help="Formula to be evaluated "
        "when generating the quantity "
        "for a production order line.\n"
        "The following values are available:\n"
        "- bom_line: the current BoM line,\n"
        "- operation: the operation where the components are"
        "consumed for current BoM line,\n"
        "- product: the Product of current BoM line,\n"
        "- product_uom: the UoM of the Product of current BoM line,\n"
        "- product_uom_qty: the quantity of the production order line,\n"
        "- production: the production order being created,\n"
        "The computed quantity "
        "must be assigned to the `quantity` variable.",
    )

    @api.constrains(
        "quantity_formula",
    )
    def _constrain_quantity_formula(self):
        for line in self:
            quantity_formula = line.quantity_formula
            if quantity_formula:
                error_message = test_python_expr(
                    expr=quantity_formula,
                    mode="exec",
                )
                if error_message:
                    raise ValidationError(error_message)

    def _quantity_formula_values(
        self,
        product,
        product_uom,
        product_uom_qty,
        production,
        operation_id=False,
    ):
        self.ensure_one()
        return {
            "bom_line": self,
            "operation": self.env["mrp.routing.workcenter"].browse(operation_id),
            "product": product,
            "product_uom": product_uom,
            "product_uom_qty": product_uom_qty,
            "production": production,
        }

    def _eval_quantity_formula(
        self,
        product,
        product_uom,
        product_uom_qty,
        production,
        operation_id=False,
    ):
        self.ensure_one()
        formula = self.quantity_formula
        if formula:
            values = self._quantity_formula_values(
                product,
                product_uom,
                product_uom_qty,
                production,
                operation_id=operation_id,
            )
            safe_eval(
                formula,
                globals_dict=values,
                mode="exec",
                nocopy=True,
            )
            quantity = values.get("quantity", 0)
        else:
            quantity = None
        return quantity
