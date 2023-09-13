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

    def check_domain(self, values):
        result = []
        for line in self.bom_line_ids.filtered(lambda s: s.execute(values)):
            if line.child_bom_id:
                result = result + line.child_bom_id.check_domain(values)
            else:
                result.append(line)

        return result

    @classmethod
    def _get_bom_domain_for_config(cls):
        "You may override me"
        return [("configuration_type", "=", "variable")]
