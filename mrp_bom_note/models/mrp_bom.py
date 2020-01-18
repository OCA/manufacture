# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    notes = fields.Html()
