# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

__name__ = "Upgrade to 11.0.2.0.0"


def _migrate_product_to_product_mrp_area(env):
    _logger.info("Migrating product parameters to Product MRP Areas")
    env.cr.execute("""
        SELECT DISTINCT mrp_area.id, pr.id, pr.mrp_applicable, pr.mrp_exclude,
        pr.mrp_inspection_delay, pr.mrp_maximum_order_qty,
        pr.mrp_minimum_order_qty, pr.mrp_minimum_stock, pr.mrp_nbr_days,
        pr.mrp_qty_multiple, pr.mrp_transit_delay, pr.mrp_verified, pr.active
        FROM product_product AS pr
        CROSS JOIN mrp_area
        LEFT JOIN product_template AS pt
        ON pt.id = pr.product_tmpl_id
        WHERE pr.mrp_exclude = False
        AND pt.type = 'product'
    """)
    product_mrp_area_model = env['product.mrp.area']
    for mrp_area_id, product_id, mrp_applicable, mrp_exclude,\
        mrp_inspection_delay, mrp_maximum_order_qty, mrp_minimum_order_qty, \
        mrp_minimum_stock, mrp_nbr_days, mrp_qty_multiple, mrp_transit_delay,\
            mrp_verified, active in env.cr.fetchall():
            product_mrp_area_model.create({
                'mrp_area_id': mrp_area_id,
                'product_id': product_id,
                'mrp_applicable': mrp_applicable,
                'mrp_exclude': mrp_exclude,
                'mrp_inspection_delay': mrp_inspection_delay,
                'mrp_maximum_order_qty': mrp_maximum_order_qty,
                'mrp_minimum_order_qty': mrp_minimum_order_qty,
                'mrp_minimum_stock': mrp_minimum_stock,
                'mrp_nbr_days': mrp_nbr_days,
                'mrp_qty_multiple': mrp_qty_multiple,
                'mrp_transit_delay': mrp_transit_delay,
                'mrp_verified': mrp_verified,
                'active': active,
            })


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _migrate_product_to_product_mrp_area(env)
