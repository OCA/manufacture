# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class MrpProductProduce(models.TransientModel):

    _inherit = 'mrp.product.produce'

    # Reload produced quants cost every consume or produce action in a MO.
    @api.multi
    def do_produce(self):
        res = super(MrpProductProduce, self).do_produce()
        production_obj = self.env['mrp.production']
        production_id = self.env.context.get('active_id', False)
        production = production_obj.browse(production_id)
        production.load_final_quant_cost()
        return res
