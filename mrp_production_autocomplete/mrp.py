# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'manuf_order_auto_complete': fields.boolean(
            'Complete Manuf. Order',
            help="Check if Manufacturing Order of this product "
                 "can be completed automatically "
                 "by a scheduled action (cron)")
    }

    _defaults = {
        'manuf_order_auto_complete': False,
    }


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def _get_autocomplete_domain(self, cr, uid, context=None):
        return [
            ('state', 'in', ['confirmed', 'ready']),
            ('product_id.manuf_order_auto_complete', '=', True),
            ]

    def complete_manufacturing_order_cron(self, cr, uid, context=None):
        _logger.debug('Search for auto-validating manufacturing order')
        domain = self._get_autocomplete_domain(cr, uid, context=context)
        mo_ids = self.search(cr, uid, domain, context=context)
        _logger.debug('Auto Validate %s manufacturing order', len(mo_ids))
        for production in self.browse(cr, uid, mo_ids, context=context):
            if production.state == 'confirmed':
                production.force_production()
            _logger.debug('Auto Validate %s', production.name)
            self.pool.get('mrp.production').action_produce(
                cr, uid, production.id, production.product_qty,
                'consume_produce', context=context)
        return True
