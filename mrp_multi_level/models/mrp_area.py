# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpArea(models.Model):
    _name = 'mrp.area'

    name = fields.Char('Name')
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse',
        required=True,
    )
    location_id = fields.Many2one(
        comodel_name='stock.location', string='Location',
        required=True,
    )
    active = fields.Boolean(default=True)
    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Working Hours',
        related='warehouse_id.calendar_id',
    )
