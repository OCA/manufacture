from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    configuration_type = fields.Selection(
        selection=[
            ("variable", "Variable BOM"),
            ("configured", "BOM from variable BOM"),
            ("normal", "Normal BOM"),
        ],
        default="normal",
        required=True,
    )

    def get_bom_configured_data(self, input_line, quantity=1.0):
        result = []
        values = input_line._get_input_line_values()
        for line in self.bom_line_ids.filtered(lambda s: s.execute(values)):
            line_quantity = (
                line.compute_qty_from_formula(input_line)
                if line.use_formula_compute_qty
                else line.product_qty
            ) * quantity
            if line.child_bom_id:
                result = result + line.child_bom_id.get_bom_configured_data(
                    input_line, line_quantity
                )
            else:
                result.append(
                    {
                        "line": line,
                        "product_qty": line_quantity,
                    }
                )

        return result

    @classmethod
    def _get_bom_domain_for_config(cls):
        "You may override me"
        return [("configuration_type", "=", "variable")]
