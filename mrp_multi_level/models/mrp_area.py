# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# © 2016-19 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar <jordi.ballester@eficent.com>
# - Lois Rilo Antelo <lois.rilo@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.base.res.res_partner import _tz_get


class MrpArea(models.Model):
    _name = 'mrp.area'

    name = fields.Char(required=True)
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse',
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='warehouse_id.company_id',
        store=True,
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
    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        default=lambda self: self._context.get(
            'tz') or self.env.user.tz or 'UTC',
        help="This field is used in order to define in which timezone "
             "the MRP Area will work.")

    @api.model
    def _datetime_to_date_tz(self, dt_to_convert=None):
        """Coverts a datetime to date considering the timezone
        of MRP Area. If no datetime is provided, it returns today's
        date in the timezone."""
        if isinstance(dt_to_convert, str):
            dt_to_convert = fields.Datetime.from_string(dt_to_convert)
        return fields.Date.context_today(
            self.with_context(tz=self.tz),
            timestamp=dt_to_convert,
        )

    @api.multi
    def _get_locations(self):
        self.ensure_one()
        return self.env['stock.location'].search([
            ('id', 'child_of', self.location_id.id)])
