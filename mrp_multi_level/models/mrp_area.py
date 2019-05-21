# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016-19 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# - Lois Rilo Antelo <lois.rilo@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpArea(models.Model):
    _name = 'mrp.area'

    name = fields.Char(required=True)
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

    @api.multi
    def _get_locations(self):
        self.ensure_one()
        return self.env['stock.location'].search([
            ('id', 'child_of', self.location_id.id)])
