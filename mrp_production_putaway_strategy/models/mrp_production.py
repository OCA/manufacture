# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_confirm(self):
        for mo in self:
            if not mo.move_prod_id:
                location = self.env['stock.location'].get_putaway_strategy(
                    mo.location_dest_id,  mo.product_id)
                if location:
                    message = _(
                        'Applied Putaway strategy to finished products '
                        'location %s.' % mo.location_dest_id.complete_name)
                    mo.message_post(message, message_type='comment')
                    mo.location_dest_id = location
        return super(MrpProduction, self).action_confirm()
