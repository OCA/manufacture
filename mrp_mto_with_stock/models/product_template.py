# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_mts_mto_location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Manufacturing MTO/MTS Locations',
        help='These manufacturing locations will create procurements when '
             'there is no stock availale in the source location.')

    @api.constrains('route_ids', 'mrp_mts_mto_location_ids')
    def _check_route_ids(self):
        for product_tmpl in self.filtered(
                lambda x: x.mrp_mts_mto_location_ids):
            if any([
                x == self.env.ref('stock.route_warehouse0_mto')
                for x in product_tmpl.route_ids
            ]):
                raise ValidationError(
                    _("'MTO' route cannot be selected with "
                      "Manufacturing MTO/MTS Locations.")
                )
