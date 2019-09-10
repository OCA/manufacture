# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_mo(self):
        """Overload to set the root and parent production order ID to the
        children production orders.
        """
        res = super(ProcurementOrder, self).make_mo()
        production_ids = [id_ for id_ in res.values() if id_]
        productions = self.env['mrp.production'].browse(production_ids)
        for production in productions:
            if self.env.context.get('parent_mrp_production_id'):
                parent_id = self.env.context['parent_mrp_production_id']
                root_id = self.env.context['root_mrp_production_id']
                production.write({
                    'parent_id': parent_id,
                    'root_id': root_id,
                })
        return res
