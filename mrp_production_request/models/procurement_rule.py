# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class ProcurementOrder(models.Model):
    _inherit = "procurement.rule"

    @api.multi
    def _prepare_mrp_production_request(
            self, product_id, product_qty, product_uom, location_id, name,
            origin, values, bom):
        self.ensure_one()
        data = self._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name,
            origin, values, bom)
        data['state'] = 'to_approve'
        orderpoint = values.get('orderpoint_id')
        if orderpoint:
            data['orderpoint_id'] = orderpoint.id
        return data

    @api.multi
    def _need_production_request(self, product_id):
        return self.action == 'manufacture' \
            and product_id.mrp_production_request

    @api.multi
    def _run_production_request(self, product_id, product_qty, product_uom,
                                location_id, name, origin, values):
        """Trying to handle this as much similar as possible to Odoo
        production orders. See `_run_manufacture` in Odoo standard."""
        request_obj = self.env['mrp.production.request']
        request_obj_sudo = request_obj.sudo().with_context(
            force_company=values['company_id'].id)
        bom = self._get_matching_bom(product_id, values)
        if not bom:
            raise UserError(_(
                'There is no Bill of Material found for the product %s. '
                'Please define a Bill of Material for this product.') % (
                product_id.display_name,))

        # create the MR as SUPERUSER because the current user may not
        # have the rights to do it (mto product launched by a sale for example)
        request = request_obj_sudo.create(
            self._prepare_mrp_production_request(
                product_id, product_qty, product_uom, location_id, name,
                origin, values, bom))
        origin_production = values.get('move_dest_ids') and \
            values['move_dest_ids'][0].raw_material_production_id or False
        orderpoint = values.get('orderpoint_id')
        if orderpoint:
            request.message_post_with_view(
                'mail.message_origin_link',
                values={'self': request,
                        'origin': orderpoint},
                subtype_id=self.env.ref('mail.mt_note').id,
            )
        if origin_production:
            request.message_post_with_view(
                'mail.message_origin_link',
                values={'self': request,
                        'origin': origin_production},
                subtype_id=self.env.ref('mail.mt_note').id,
            )
        return True

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values):
        if self._need_production_request(product_id):
            return self._run_production_request(
                product_id, product_qty, product_uom,
                location_id, name, origin, values)

        return super()._run_manufacture(
            product_id, product_qty, product_uom, location_id, name,
            origin, values)
