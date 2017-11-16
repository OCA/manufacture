# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        sale_proc = procurement.move_dest_id.procurement_id
        mrp_notes = sale_proc.sale_line_id.order_id.partner_id.mrp_notes
        if mrp_notes:
            old = (
                res.get('notes') and
                ('{other}\n'.format(other=res.get('notes', ''))) or '')
            res['notes'] = '{old}{mine}'.format(old=old, mine=mrp_notes)
        return res
