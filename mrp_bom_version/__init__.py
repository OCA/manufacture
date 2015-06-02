# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from . import models
from openerp import SUPERUSER_ID


def set_bom_inactive(cr, registry):
    """Set all draft or historical state BoMs inactive."""
    mrp_bom_obj = registry['mrp.bom']
    mrp_bom_ids = mrp_bom_obj.search(cr, SUPERUSER_ID,
                                     [('active', '=', True)])
    for mrp_bom in mrp_bom_obj.browse(cr, SUPERUSER_ID, mrp_bom_ids):
        mrp_bom_obj.write(cr, SUPERUSER_ID, mrp_bom.id, {'state': 'active'})
