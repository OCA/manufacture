from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    configuration_type = fields.Selection([
        ('variable', 'Variable BOM'),
        ('configured', 'BOM from variable BOM'), ('normal', 'Normal BOM')], 'Configuration Type',
        default='normal', required=True)

    def check_domain(self, values):
        result = []
        for line in self.bom_line_ids.filtered(lambda s: s.execute(values)):
            if line.child_bom_id:
                result = result + line.child_bom_id.check_domain(values)
            else:
                result.append(line)

        return result
