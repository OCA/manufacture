# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, SUPERUSER_ID


def create_default_routing_workcenter_line(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        routing_wcs = env['mrp.routing.workcenter'].search(
            [('op_wc_lines', '=', False)])
        for routing_wc in routing_wcs:
            routing_wc.op_wc_lines = [
                (0, 0, {'workcenter': routing_wc.workcenter_id,
                        'default': True,
                        'custom_data': True})]


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
    create_default_routing_workcenter_line(cr)
