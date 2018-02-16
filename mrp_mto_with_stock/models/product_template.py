# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_mts_mto_location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Manufacturing MTO/MTS Locations',
        help='These manufacturing locations will create procurements when '
             'there is no stock availale in the source location.')
