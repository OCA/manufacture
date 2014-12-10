# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from . import models
from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    # Create QC triggers
    picking_type_ids = registry['stock.picking.type'].search(
        cr, SUPERUSER_ID, [])
    for picking_type_id in picking_type_ids:
        registry['stock.picking.type']._create_qc_trigger(
            cr, SUPERUSER_ID, picking_type_id)
