# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openerp import models, api

_logger = logging.getLogger(__name__)


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

        for move in production.move_created_ids2:
            prod_lots = move.lot_ids
            prod_lots.write({'bom_id': production.bom_id.id})

        return res
