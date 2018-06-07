# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpInventory(models.Model):
    _name = 'mrp.inventory'

    mrp_area_id = fields.Many2one('mrp.area', 'MRP Area',
                                  related='mrp_product_id.mrp_area_id')
    mrp_product_id = fields.Many2one('mrp.product', 'Product',
                                     select=True)
    date = fields.Date('Date')
    demand_qty = fields.Float('Demand')
    supply_qty = fields.Float('Supply')
    initial_on_hand_qty = fields.Float('Starting Inventory')
    final_on_hand_qty = fields.Float('Forecasted Inventory')
    to_procure = fields.Float('To procure')

    _order = 'mrp_product_id, date'
