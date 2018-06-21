# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    mrp_area_id = fields.Many2one(
        comodel_name='mrp.area', string='MRP Area',
        help="Requirements for a particular MRP area are combined for the "
             "purposes of procurement by the MRP.",
    )
