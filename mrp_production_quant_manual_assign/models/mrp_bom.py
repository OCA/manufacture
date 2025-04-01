# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    # TODO: Remove this in v18 migration as the computes for manual
    #  consumption has been removed in that version and readonly field is deleted also.
    #  https://github.com/odoo/odoo/blob/18.0/addons/mrp/models/mrp_bom.py#L622
    manual_consumption = fields.Boolean(compute=None, default=False)
    manual_consumption_readonly = fields.Boolean(compute=None, default=False)
