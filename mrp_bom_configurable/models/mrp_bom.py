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

    def _compute_data_from_line_and_quantity(self, line, line_quantity):
        return {
            "product_tmpl_id": line.product_tmpl_id,
            "product_id": line.product_id,
            "product_qty": line_quantity,
            "product_uom_id": line.product_uom_id,
        }

    def get_bom_configured_data(self, input_line, quantity=1.0):
        result = []
        values = input_line._get_input_line_values()
        for line in self.bom_line_ids.filtered(lambda s: s.check_domain(values)):
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
                    self._compute_data_from_line_and_quantity(line, line_quantity)
                )

        return result

    @classmethod
    def _get_bom_domain_for_config(cls):
        "You may override me"
        return [("configuration_type", "=", "variable")]

    def find_parent_bom_in_exploded(self, boms_done, parent_bom_id):
        parent_bom_data = False
        for bom, bom_data in boms_done:
            if bom.id == parent_bom_id.id:
                parent_bom_data = bom_data
        return parent_bom_data

    def _recompute_variable_quantity(self, quantity, input_line, boms_done, lines_done):
        for bom, bom_data in boms_done:
            if bom_data["parent_line"] and bom_data["parent_line"].use_formula_compute_qty:
                bom_data["qty"] = bom_data["original_qty"] * bom_data[
                    "parent_line"
                ].compute_qty_from_formula(input_line)

        for bom_line, line_data in lines_done:
            parent_line = line_data["parent_line"]

            parent_quantity = 1
            if line_data["parent_line"] and parent_line.bom_id.type == "phantom":
                parent_bom_data = self.find_parent_bom_in_exploded(
                    boms_done, line_data["parent_line"].bom_id
                )
                parent_quantity = parent_bom_data["qty"]

            line_data["qty"] = parent_quantity * line_data["qty"]

            if bom_line.use_formula_compute_qty:
                line_data["qty"] = (
                    line_data["qty"]
                    * bom_line.compute_qty_from_formula(input_line)
                )

            while parent_line and parent_line.bom_id.type == "phantom":
                parent_bom_data = False
                for bom, bom_data in boms_done:
                    if bom.id == parent_line.bom_id.id:
                        parent_bom_data = bom_data
                if parent_bom_data:
                    line_data["parent_line"] = parent_bom_data["parent_line"]
                    parent_line = line_data["parent_line"]
                else:
                    break

    def explode(self, product, quantity, picking_type=False):
        boms_done, lines_done = super().explode(product, quantity, picking_type)
        input_line_id = self.env.context.get("input_line_id", False)
        if input_line_id:
            input_line = self.env["input.line"].browse(input_line_id)
            self._recompute_variable_quantity(
                quantity, input_line, boms_done, lines_done
            )
        return boms_done, lines_done

