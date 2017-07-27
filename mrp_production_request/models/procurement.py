# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    mrp_production_request_id = fields.Many2one(
        comodel_name="mrp.production.request", string="Manufacturing Request",
        copy=False)

    @api.model
    def _prepare_mrp_production_request(self, procurement):
        data = self._prepare_mo_vals(procurement)
        data['procurement_id'] = procurement.id
        data['state'] = 'to_approve'
        return data

    @api.model
    def _run(self, procurement):
        if (procurement.rule_id and
                procurement.rule_id.action == 'manufacture' and
                procurement.product_id.mrp_production_request):
            if not procurement.check_bom_exists():
                procurement.message_post(
                    body=_("No BoM exists for this product!"))
                return False
            if not self.mrp_production_request_id:
                request_data = self._prepare_mrp_production_request(
                    procurement)
                req = self.env['mrp.production.request'].create(request_data)
                procurement.message_post(body=_(
                    "Manufacturing Request created"))
                procurement.mrp_production_request_id = req.id
            return True
        return super(ProcurementOrder, self)._run(procurement)

    @api.multi
    def propagate_cancels(self):
        result = super(ProcurementOrder, self).propagate_cancels()
        for procurement in self:
            mrp_production_requests = \
                self.env['mrp.production.request'].sudo().search([
                    ('procurement_id', '=', procurement.id)])
            if mrp_production_requests and not self.env.context.get(
                    'from_mrp_production_request'):
                mrp_production_requests.sudo().button_cancel()
                for mr in mrp_production_requests:
                    mr.sudo().message_post(
                        body=_("Related procurement has been cancelled."))
            procurement.write({'mrp_production_request_id': None})
        return result
