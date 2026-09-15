from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        res = super().action_confirm()
        for bom_line in self.bom_id.bom_line_ids:
            if bom_line.component_template_id:
                # product_id was set in mrp.bom.explode for correct flow.
                # Need to remove it.
                bom_line.product_id = False
        return res

    @api.constrains("bom_id")
    def _check_component_attributes(self):
        self.bom_id._check_component_attributes()
