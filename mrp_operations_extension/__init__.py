# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models
from . import wizard


def post_init_hook(cr, pool):
    """ Set do_production on the last workcenter line of each routing """
    cr.execute(
        """
        UPDATE mrp_routing_workcenter SET do_production = TRUE
        WHERE id IN (
            SELECT (
                SELECT id FROM mrp_routing_workcenter WHERE routing_id = mr.id
                ORDER BY sequence DESC, id DESC LIMIT 1)
            FROM mrp_routing mr);
        """)
