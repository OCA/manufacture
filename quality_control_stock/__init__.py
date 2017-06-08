# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from . import models
from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    # Create QC triggers
    picking_type_ids = registry['stock.picking.type'].search(
        cr, SUPERUSER_ID, [])
    for picking_type_id in picking_type_ids:
        registry['stock.picking.type']._create_qc_trigger(
            cr, SUPERUSER_ID, picking_type_id)
