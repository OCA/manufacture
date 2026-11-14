# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    has_owner = fields.Boolean()
