# -*- coding: utf-8 -*-
# (c) 2015 Savoir-faire Linux - <http://www.savoirfairelinux.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_produce(self, production_id, production_qty,
                       production_mode, wiz=False):
        """Affect the Bill of Material to each serial number related to
        the produced stocks
        """
        res = super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz)
        production = self.browse(production_id)
        prod_lots = production.mapped('move_created_ids2.lot_ids')
        prod_lots.write({'bom_id': production.bom_id.id})
        return res
