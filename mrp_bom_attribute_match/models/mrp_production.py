from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        if self and self.bom_id:
            for bom_line in self.bom_id.bom_line_ids:
                if bom_line.component_template_id:
                    # product_id was set in mrp.bom.explode for correct flow. Need to remove it.
                    bom_line.product_id = False
        return res

    def write(self, vals):
        for bl in self.bom_id.bom_line_ids.filtered(lambda x: x.component_template_id):
            bl.check_component_attributes()
        return super(MrpProduction, self).write(vals)
