# Copyright 2016-19 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        res = super(MrpProductProduce, self).do_produce()
        if self.production_id.company_id.mrp_production_auto_post_inventory:
            if self.production_id.company_id.mrp_production_auto_post_inventory_cron:
                self.production_id.to_post_inventory_cron = True
            else:
                self.production_id.post_inventory()
        return res
