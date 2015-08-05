# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        notes = res.get('notes', '')
        sale_proc = procurement.move_dest_id.procurement_id
        notes += ('|n%s' %
                  (sale_proc.sale_line_id.order_id.partner_id.mrp_notes or ''))
        res['notes'] = notes
        return res
