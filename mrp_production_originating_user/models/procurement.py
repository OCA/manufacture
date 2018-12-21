# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    origin_user_id = fields.Many2one('res.users', 'Responsible',
                                     default=lambda self: self._uid)

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values):
        Production = self.env['mrp.production']
        ProductionSudo = Production.sudo().with_context(
            force_company=values['company_id'].id)
        bom = self._get_matching_bom(product_id, values)
        if not bom:
            msg = _(
                'There is no Bill of Material found for the product %s. '
                'Please define a Bill of Material for this product.') % (
                product_id.display_name,)
            raise UserError(msg)

        # create the MO as SUPERUSER because the current user may not have
        # the rights to do it (mto product launched by a sale for example)
        production = ProductionSudo.create(
            self._prepare_mo_vals(product_id, product_qty, product_uom,
                                  location_id, name, origin, values, bom))
        origin_production = values.get('move_dest_ids') and values[
            'move_dest_ids'][0].raw_material_production_id or False
        orderpoint = values.get('orderpoint_id')
        self.origin_user_id = orderpoint.create_uid
        if orderpoint:
            production.message_post_with_view(
                'mail.message_origin_link',
                values={'self': production,
                        'origin': orderpoint},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        if origin_production:
            production.message_post_with_view(
                'mail.message_origin_link',
                values={'self': production,
                        'origin': origin_production},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return True

    def _prepare_mo_vals(self, product_id, product_qty,
                         product_uom, location_id, name,
                         origin, values, bom):

        res = super(ProcurementRule, self)._prepare_mo_vals(product_id,
                                                            product_qty,
                                                            product_uom,
                                                            location_id, name,
                                                            origin, values,
                                                            bom)
        res.update({'user_id': self.origin_user_id.id})
        return res
